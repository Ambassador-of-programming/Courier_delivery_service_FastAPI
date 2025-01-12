from models.auth_model import LoginModel, SignupModel, CreateTokenModel
from config.database import AuthDataBase, OrderProductDatabase
from config.create_token_check import TOKEN_CHECK
from fastapi import APIRouter, Security
from config.jwt_token import JwtManager


# Создаем роутер для пользователей
auth_router = APIRouter()
jwt = JwtManager()

# POST запрос на авторизацию
@auth_router.post("/signin")
async def signin_user(login: LoginModel) -> dict:
    db = AuthDataBase()
    result = await db.signin_user(
        phone_number=login.phone_number, password=login.password)
    
    if result != None:
        return {
            "message": True,
            "result": result,
            "jwt_token": await jwt.create_token()  # Создаем JWT-токен для пользователя
        }
    
    else:
        return {
            "message": False
        }

# POST запрос на регистрацию
@auth_router.post("/signup")
async def signup_user(signup: SignupModel, jwt_token: dict = Security(jwt.verify_token)):
    db = AuthDataBase()

    result = await db.signup_user(
        phone_number=signup.phone_number, password=signup.password, fio=signup.fio,
    )
    
    if result != None:
        return {
            "message": True,
            "result": result
        }
    
    else:
        return {
            "message": False
        }
    
@auth_router.post("/create_jwt_token")
async def create_jwt_token(token: CreateTokenModel):
    # Проверяем, есть ли результаты запроса
    result = token.token

    if result == TOKEN_CHECK:
        tokens = await jwt.create_token()
        return {
            "message": True,
            "jwt_token": tokens
        }
    
    else:
        return {
            "message": False
        }
    
@auth_router.get("/create_db")
async def create_db(token: str):
    # Проверяем, есть ли результаты запроса
    result = token

    if result == TOKEN_CHECK:
        auth = AuthDataBase()
        await auth.create_db()

        order_product = OrderProductDatabase()
        await order_product.create_db()

        return {
            "message": True,
        }
    
    else:
        return {
            "message": False
        }