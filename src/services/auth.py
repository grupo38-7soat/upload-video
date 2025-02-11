import os
import jwt

from src.utils.exceptions import handle_unauthorized_exception


class JWTService:
    def decode_jwt(self, token: str):
        try:
            payload = jwt.decode(token, {os.getenv("JWT_SECRET")}, algorithms=['HS256'], options={"verify_signature": False})
            user_id = payload.get("id")
            if user_id:
                return user_id
        except jwt.ExpiredSignatureError as e:
            handle_unauthorized_exception(f'Erro ao obter o token: {e}')
        except jwt.InvalidTokenError as e:
            handle_unauthorized_exception(f'Erro ao obter o token: {e}')
        except Exception as e:
            handle_unauthorized_exception(f'Erro ao obter o token: {e}')
