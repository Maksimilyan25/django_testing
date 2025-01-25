from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    """Анониму доступна главная страница и авторизация."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_name',
    ('news:detail',)
)
def test_detail_pages_for_anonymous(client, url_name, news):
    """Аноним, может просматривать детально новости."""
    url = reverse(url_name, args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',)
)
def test_comment_edit_and_del_for_author(author_client, name, comment):
    """Страница для автора, может ред. и удалять свои комментарии."""
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


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


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',)
)
def test_not_author_cant_del_idet_comment(not_author_client, name, comment):
    """Тест страницы, юзер не может удалять и ред. чужие комменты."""
    url = reverse(name, args=(comment.id,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
