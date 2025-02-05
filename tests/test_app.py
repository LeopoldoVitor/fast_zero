from http import HTTPStatus
from schemas import UserPublic
from security import create_access_token


def test_read_root_dedve_retornar_OK_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Ola, Mundo'}


def test_create_user_deve_retornar_user_com_id(client):
    response = client.post(
        '/users/',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_db(client, user):
    response = client.get('/users/')

    user_schema = UserPublic.model_validate(user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_one_user_deve_retornar_user(client, user):
    response = client.get('/users/1')

    user_schema = UserPublic.model_validate(user).model_dump()

    assert response.json() == user_schema


def test_read_one_user_deve_retornar_user_not_found(client):
    response = client.get('/users/2')

    assert response.json() == {'detail': 'User not found'}


def test_update_user_deve_atualizar_o_usuario_1(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'test_atualizado',
            'email': 'test_atualizado@test.com',
            'password': 'test',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'test_atualizado',
        'email': 'test_atualizado@test.com',
        'id': 1,
    }


def test_update_user_deve_retornar_not_enough_permissions(client, user, token):
    response = client.put(
        'users/2',
        json={
            'username': 'test_atualizado',
            'email': 'test_atualizado@test.com',
            'password': 'test',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_deve_retornar_username_alredy_exists(client, user, token):
    response = client.put(
        f'users/{user.id}',
        json={
            'username': 'test',
            'email': 'test_atualizado@test.com',
            'password': 'test',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == {'detail': 'Username alredy exists'}


def test_update_user_deve_retornar_email_alredy_exists(client, user, token):
    response = client.put(
        f'users/{user.id}',
        json={
            'username': 'test_atualizado',
            'email': 'test@test.com',
            'password': 'test',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == {'detail': 'Email alredy exists'}


def test_delete_user_deve_retornar_user_deleted(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'message': 'User deleted'}


def test_delete_user_deve_retornar_not_enough_permissions(client, user, token):
    response = client.delete(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_token_invalid(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer '},
    )
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_found(client):
    data = {'sub': 'no@email.com'}
    token = create_access_token(data)
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'bearer'
    assert 'access_token' in token


def test_get_token_deve_retornar_incorrect_email_or_password(client, user):
    response = client.post(
        '/token',
        data={'username': 'test', 'password': 'test'}
    )

    assert response.json() == {'detail': 'Incorrect email or password'}
