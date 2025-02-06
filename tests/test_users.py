from http import HTTPStatus
from schemas import UserPublic


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


def test_update_user_deve_retornar_username_alredy_exists(
    client, user, other_user, token
):
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


def test_update_user_deve_retornar_email_alredy_exists(
    client, user, other_user, token
):
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


def test_user_permissions(client, user, other_user, token):
    response = client.delete(
        f'users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_deve_retornar_user_deleted(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'message': 'User deleted'}
