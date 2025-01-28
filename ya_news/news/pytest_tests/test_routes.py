import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db

CLIENT = Client()


@pytest.mark.parametrize('route_name, user_client', [
    ('news:home', CLIENT),
    ('users:login', CLIENT),
    ('users:logout', CLIENT),
    ('users:signup', CLIENT),
    ('news:detail', CLIENT),
    ('news:edit', pytest.lazy_fixture('author_client')),
    ('news:delete', pytest.lazy_fixture('author_client')),
])
def test_anonymous_user_access(route_name, user_client, anonymous_routes):
    """Тест доступности страниц для анонимного пользователя."""
    args, expected_status = anonymous_routes[route_name]
    url = reverse(route_name, args=args)
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    [
        (pytest.lazy_fixture('redirect_edit_comment')),
        (pytest.lazy_fixture('redirect_del_comment')),
    ]
)
def test_redirect_anonymous_cant_edit_and_del_comment(client, all_routes, url):
    """Редирект анонима на страницу авторизации."""
    login_url = all_routes['login']
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
