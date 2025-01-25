import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from news.models import Comment
from news.forms import WARNING, BAD_WORDS

@pytest.mark.django_db
def test_cant_add_comment_anonymous(client, form_data, news):
    """Тест, аноним не может отправить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_login = f'{login_url}?next={url}'
    assertRedirects(response, expected_login)
    assert Comment.objects.count() == 0


def test_can_add_comment_users(author, author_client, form_data, news):
    """тест, что юзеры и автор могут отправить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    redirect_url = f'{url}#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author

def test_bad_words_and_warning_in_comment(not_author_client, form_data, news):
    """Тест, что комментарий с плохими словами не проходит валидацию."""
    form_data['text'] = BAD_WORDS
    url = reverse('news:detail', args=(news.pk,))
    response = not_author_client.post(url, data=form_data)
    assert Comment.objects.count() == 0
    assert response.status_code == 200
    assert WARNING in response.context['form'].errors['text']


def test_users_can_edit_comment(
        author_client, form_data, news, comment
        ):
    """Тест, авторы могут редактировать комментарии."""
    url = reverse('news:edit', args=(news.pk,))
    response = author_client.post(url, form_data)
    redirect_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_users_cant_edit_com(not_author_client, form_data, comment):
    """Тест, юзеры не могут редактировать чужие комменты."""
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_users_cant_delete_com(not_author_client, comment):
    """Тест, юзеры не могут удалять чужие комменты."""
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_authors_can_delete_com(author_client, news, comment):
    """Тест, авторы могут удалять свои комменты."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    redirect_url = reverse('news:detail', args=(news.pk,)) + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0
