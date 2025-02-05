from models import User
from sqlalchemy import select


def test_create_user_db(session):
    user = User(username='vitor', email='vitor@test.com', password='senha123')

    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.email == 'vitor@test.com'))
    assert result.id == 1
