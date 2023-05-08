import requests
from typing import Literal
import json
from tests.config import API_URL


session = requests.Session()


class ApiError(Exception):
    def __init__(self, status_code: int, message: dict | str):
        self.status_code = status_code
        self.message = message


def basic_request(
        method: Literal['get', 'post', 'patch', 'delete'],
        path: str,
        *args,
        **kwargs
        ) -> dict:
    print(f"{API_URL}{path}")
    method = getattr(session, method)
    response = method(f'{API_URL}{path}', *args, **kwargs)
    if response.status_code >= 400:
        try:
            message = response.json()
        except json.decoder.JSONDecodeError:
            message = response.text
        raise ApiError(response.status_code, message)
    return response.json()


def create_user(name: str, admin: bool, psw: str, mail: str):
    return basic_request('post', '/user/', json={'name': name,
                                                 'admin': admin,
                                                 'psw': psw,
                                                 'mail': mail}
                         )


def create_adv(owner_id: int, title: str, description: str):
    return basic_request('post',
                         '/user/adv/',
                         json={'owner_id': owner_id,
                               'title': title,
                               'description': description
                               }
                         )


def get_user(user_id: int):
    return basic_request('get', f'/user/{user_id}')


def get_adv(adv_id: int):
    return basic_request('get', f'/user/adv/{adv_id}')


def patch_user(user_id: int, patch: dict):
    return basic_request('patch', f'/user/{user_id}', json=patch)


def patch_adv(adv_id: int, patch: dict, token: str):
    return basic_request('patch',
                         f'/user/adv/{adv_id}',
                         json=patch,
                         headers={'token': token}
                         )


def delete_user(user_id: int, token: str):
    return basic_request('delete',
                         f'/user/{user_id}',
                         headers={'token': token}
                         )


def delete_adv(adv_id: int, token: str):
    return basic_request('delete',
                         f'/user/adv/{adv_id}',
                         headers={'token': token}
                         )


def login(name: str, psw: str):
    return basic_request('post',
                         '/login',
                         json={'name': name, 'psw': psw}
                         )
