from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User
from app.core.security import hash_password
from app.schemas.users import CreateUserRequest, CreateUserResponse

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