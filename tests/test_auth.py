from http import HTTPStatus


def test_get_token_deve_retornar_incorrect_email_or_password(client, user):
    response = client.post(
        '/auth/token', data={'username': 'test', 'password': 'test'}
    )

    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'bearer'
    assert 'access_token' in token
