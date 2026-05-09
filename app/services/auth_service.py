from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, LoginResponse, JWTToken, RefreshTokenRequest, RefreshTokenResponse

class AuthService:
    async def login(self, user_login: LoginRequest, db: AsyncSession) -> LoginResponse:
        try:
            user_result = await db.execute(select(User).where(User.email == user_login.email))
            user = user_result.scalar_one_or_none()

            if not user or not verify_password(user_login.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )
            
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            user.fcm_token = user_login.fcm_token
            await db.commit()
            await db.refresh(user)

            return LoginResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                cnic_image_url=user.cnic_image_url,
                status=user.status,
                jwt=JWTToken(access_token=access_token, refresh_token=refresh_token)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

    async def refresh_token(self, refresh_token: RefreshTokenRequest, db: AsyncSession) -> RefreshTokenResponse:
        try:
            user_id = decode_token(refresh_token.refresh_token, token_type="refresh")
            user = await db.get(User, user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            
            new_access_token = create_access_token(user.id)
            new_refresh_token = create_refresh_token(user.id)

            return RefreshTokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )