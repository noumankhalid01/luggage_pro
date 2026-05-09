from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.core.security import hash_password
from app.schemas.users import CreateUserRequest, CreateUserResponse, UpdateMeRequest, UpdateMeResponse

class UserService:

    async def create_user(self, user_data: CreateUserRequest, db: AsyncSession) -> CreateUserResponse:
        try:
            existing_user_stmt = select(User).where(
                or_(User.email == user_data.email, User.phone == user_data.phone)
            )
            duplicate = await db.scalar(existing_user_stmt)
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or phone already registered",
                )
            
            hashed_password = hash_password(user_data.password)
            new_user = User(
                full_name=user_data.full_name.lower(),
                email=user_data.email,
                phone=user_data.phone,
                password_hash=hashed_password,
                cnic_image_url=user_data.cnic_image_url,
                fcm_token=user_data.fcm_token,
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            return CreateUserResponse(
                id=new_user.id,
                full_name=new_user.full_name,
                email=new_user.email,
                phone=new_user.phone,
                cnic_image_url=new_user.cnic_image_url,
                fcm_token=new_user.fcm_token,
                status=new_user.status.value,
            )
        except HTTPException:
            raise 
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def update_me(
        self,
        current_user: User,
        user_data: UpdateMeRequest,
        db: AsyncSession,
    ) -> UpdateMeResponse:
        try:
            updates = user_data.model_dump(exclude_unset=True)

            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="At least one field must be provided",
                )

            duplicate_conditions = []
            if "email" in updates:
                duplicate_conditions.append(User.email == updates["email"])
            if "phone" in updates:
                duplicate_conditions.append(User.phone == updates["phone"])

            if duplicate_conditions:
                duplicate_stmt = select(User).where(
                    or_(*duplicate_conditions),
                    User.id != current_user.id,
                )
                duplicate = await db.scalar(duplicate_stmt)
                if duplicate:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email or phone already registered",
                    )

            if "full_name" in updates:
                current_user.full_name = updates["full_name"].lower()
            if "email" in updates:
                current_user.email = updates["email"]
            if "phone" in updates:
                current_user.phone = updates["phone"]

            await db.commit()
            await db.refresh(current_user)

            return UpdateMeResponse(
                id=current_user.id,
                full_name=current_user.full_name,
                email=current_user.email,
                phone=current_user.phone,
                cnic_image_url=current_user.cnic_image_url,
                status=current_user.status.value,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )
