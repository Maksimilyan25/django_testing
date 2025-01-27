from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


FORM_DATA = {
    'text': 'текст'
}
FORM_BAD_WORDS = {
    'text': 'текст'
}

pytestmark = pytest.mark.django_db


def test_cant_add_comment_anonymous(client, all_routes, news):
    """Тест, аноним не может отправить комментарий."""
    url = reverse(all_routes[1], args=(news.pk,))
    first_comment_count = Comment.objects.count()
    response = client.post(url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_login = f'{login_url}?next={url}'
    assertRedirects(response, expected_login)
    assert Comment.objects.count() == first_comment_count


def test_can_add_comment_users(author, author_client, all_routes, news):
    """тест, что юзеры и автор могут отправить комментарий."""
    url = reverse(all_routes[1], args=(news.pk,))
    first_comment_count = Comment.objects.count()
    assert first_comment_count == 0
    response = author_client.post(url, data=FORM_DATA)
    redirect_url = f'{url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_bad_words_and_warning_in_comment(not_author_client, all_routes, news):
    """Тест, что комментарий с плохими словами не проходит валидацию."""
    FORM_BAD_WORDS['text'] = BAD_WORDS
    url = reverse(all_routes[1], args=(news.pk,))
    response = not_author_client.post(url, data=FORM_BAD_WORDS)
    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']


def test_users_can_edit_comment(
        author_client, all_routes, news, comment
):
    """Тест, авторы могут редактировать комментарии."""
    url = reverse(all_routes[2], args=(news.pk,))
    response = author_client.post(url, FORM_DATA)
    redirect_url = reverse(all_routes[1], args=(news.pk,)) + '#comments'
    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.author == comment.author
    assert comment.news == news


def test_users_cant_edit_com(not_author_client, all_routes, news, comment):
    """Тест, юзеры не могут редактировать чужие комменты."""
    url = reverse(all_routes[2], args=(comment.id,))
    response = not_author_client.post(url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment.author
    assert comment.news == news


def test_users_cant_delete_com(not_author_client, all_routes, comment):
    """Тест, юзеры не могут удалять чужие комменты."""
    url = reverse(all_routes[3], args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_authors_can_delete_com(author_client, all_routes, news, comment):
    """Тест, авторы могут удалять свои комменты."""
    url = reverse(all_routes[3], args=(comment.id,))
    response = author_client.post(url)
    redirect_url = reverse(all_routes[1], args=(news.pk,)) + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0
