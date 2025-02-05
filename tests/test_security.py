from security import create_access_token


def test_get_current_user_no_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer'},
    )
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_invalid(client):
    data = {'sub': 'no@email.com'}
    token = create_access_token(data)
    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json() == {'detail': 'Could not validate credentials'}
