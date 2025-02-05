from security import create_access_token, SECRET_KEY, ALGORITHM
from jwt import decode


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded['sub'] == data['sub']
    assert decoded['exp']
