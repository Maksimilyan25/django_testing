from django.urls import reverse
from pytest_django.asserts import assertRedirects
import pytest


pytestmark = pytest.mark.django_db


def test_anonymous_user_access(anonymous_routes, news):
    """Тест доступности страниц для анонимного пользователя."""
    for route, users, status in anonymous_routes:
        url = reverse(route, args=(news.pk,) if route == 'news:detail' else [])
        response = users.get(url)
        assert response.status_code == status


def test_comment_edit_and_del(client_routes, comment):
    """Тест страницы для редактирования и удаления комментариев."""
    for name, users, status in client_routes:
        url = reverse(name, args=(comment.id,))
        response = users.get(url)
        assert response.status_code == status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',)
)
def test_redirect_anonymous_cant_edit_and_del_comment(client, name, comment):
    """Редирект анонима на страницу авторизации."""
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
