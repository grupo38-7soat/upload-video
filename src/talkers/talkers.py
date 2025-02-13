import os
from aiohttp import ClientSession

from utils.exceptions import handle_default_error_exception


class Talker:
    # Função assíncrona para fazer a requisição com o JWT
    @staticmethod
    async def retrieve_user(user_id):
        url = f'{os.getenv("USER_API_URL")}/usuarios/{user_id}'

        headers = {
            'Content-Type': 'application/json'
        }

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    handle_default_error_exception('Erro ao retornar os dados usuário')


