import requests
import pytest
from tests.config import API_URL
from tests import api


def test_login(new_user):
    token = api.login(new_user['name'], new_user['psw'])['token']
    assert isinstance(token, str)


def test_root():
    response = requests.get(f'{API_URL}')
    assert response.status_code == 404


def test_create_user():
    new_user = api.create_user('user1',
                               True,
                               'password1',
                               'qwerty@qwer.ru'
                               )
    assert 'id' in new_user


def test_create_adv(new_user):
    new_adv = api.create_adv(new_user['id'],
                             'titlyatina',
                             'descriptyatina'
                             )
    assert 'adv_id' in new_adv


def test_get_user(root_user):
    user = api.get_user(root_user['id'])
    assert user['name'] == root_user['name']


def test_get_adv(new_adv):
    adv = api.get_adv(new_adv['id'])
    assert adv['id'] == new_adv['id']


def test_user_non_existed():
    with pytest.raises(api.ApiError) as err_info:
        api.get_user(999999)
    assert err_info.value.status_code == 404
    assert err_info.value.message == {
        'status': 'error',
        'message': 'User not found'
        }


def test_patch_adv(new_user, new_adv):
    token = api.login(new_user['name'], new_user['psw'])['token']
    response = api.patch_adv(new_adv['id'],
                             patch={'title': 'tit',
                                    'description': 'deskript'},
                             token=token
                             )
    assert response == {'status': 'success'}


def test_delete_adv(new_user, new_adv):
    token = api.login(new_user['name'], new_user['psw'])['token']
    response = api.delete_adv(new_adv['id'], token=token)
    assert response == {'status': 'delete'}
    with pytest.raises(api.ApiError) as err_info:
        api.get_adv(new_adv['id'])
    assert err_info.value.status_code == 404
    assert err_info.value.message == {'status': 'error',
                                      'message': 'Advertising not found'
                                      }


def test_delete_user(new_user):
    token = api.login(new_user['name'], new_user['psw'])['token']
    response = api.delete_user(new_user['id'], token=token)
    assert response == {'status': 'delete'}
    with pytest.raises(api.ApiError) as err_info:
        api.get_user(new_user['id'])
    assert err_info.value.status_code == 404
    assert err_info.value.message == {'status': 'error',
                                      'message': 'User not found'
                                      }


def test_patch_user(root_user):
    response = api.patch_user(root_user['id'],
                              patch={'name': 'ppp',
                                     'admin': False,
                                     'psw': '1234',
                                     'mail': 'ryba-rak@mail.su'}
                              )
    assert response == {'status': 'success'}
    user = api.get_user(root_user['id'])
    assert user['name'] == 'ppp'
