from conftest import TodoFactory
from models import TodoState
from http import HTTPStatus


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'title',
            'description': 'description',
            'state': 'todo',
        },
    )

    assert response.json() == {
        'title': 'title',
        'description': 'description',
        'state': 'todo',
        'id': 1,
    }


def test_read_todos(client, token, todos):
    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {
        'todos': [
            {
                'id': 1,
                'title': 'test',
                'description': 'testtest',
                'state': 'todo',
            }
        ]
    }


def test_read_todos_should_return_5_todos(client, session, token, user):
    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


def test_read_todos_pagination_should_return_2_todos(
    client, session, token, user
):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_read_todos_filter_title_should_return_5_todos(
    client, session, token, user
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, title='test title')
    )
    session.commit()

    response = client.get(
        '/todos/?title=test title',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_read_todos_filter_description_should_return_5_todos(
    client, session, token, user
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5, user_id=user.id, description='test description'
        )
    )
    session.commit()

    response = client.get(
        '/todos/?description=test description',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_read_todos_filter_state_should_return_5_todos(
    client, session, token, user
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.todo)
    )
    session.commit()

    response = client.get(
        '/todos/?state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_read_todos_combined(client, session, user, token):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='test title',
            description='test description',
            state=TodoState.todo,
        )
    )
    session.commit()

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='test title',
            description='desc',
            state=TodoState.doing,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=test title&description=test description&state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_delete_todo(client, token, user, todos):
    response = client.delete(
        f'/todos/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task deleted'}


def test_delete_todo_should_return_task_not_found(
    client, token, user, other_user, todos
):
    response = client.delete(
        f'/todos/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}
