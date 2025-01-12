from fastapi import  HTTPException, status, Security
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer
from jose import JWTError, jwt


class JwtManager():
    def __init__(self):
        self.SECRET_KEY = "0f8506a2feeae271fc2cac3b07bd4222f76e362d79e9"
        self.ALGORITHM = "HS256"
        self.ACCES_TOKEN_EXPIRE_MITUTES = 30000

    async def create_token(self):
        payload = {
            "iat": datetime.now(tz=timezone.utc),  # Время создания токена
            "exp": datetime.now(tz=timezone.utc) + ( timedelta(minutes=self.ACCES_TOKEN_EXPIRE_MITUTES)),  # Время истечения токена
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def verify_token(self, credentials = Security(HTTPBearer())):
        try:
            token = credentials.credentials  # Извлекаем строку токена из HTTPAuthorizationCredentials
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
