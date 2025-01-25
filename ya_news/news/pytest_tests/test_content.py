import pytest

from http import HTTPStatus

from django.urls import reverse

from news.forms import CommentForm


HOME_PAGES = 10


def test_pages_paginator(client, create_news):
    """Тест количества новостей на странице."""
    url = reverse('news:home')
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
    # Проверим, что на странице не более 10 новостей
    assert len(response.context['news_list']) <= HOME_PAGES


def test_order_news_on_page(client, create_news):
    """Тест, сортировка новостей по убыванию."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert response.status_code == HTTPStatus.OK
    assert all_dates == sorted_dates


def test_order_comment_in_news(client, news, create_comments):
    """Тест сортировка по возрастанию комментов."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'name, have_form',
    [
        (pytest.lazy_fixture('not_author_client'), True),  # пользователь
        (pytest.lazy_fixture('author_client'), True),  # автор
        (pytest.lazy_fixture('client'), False)  # анонимный
    ]
)
def test_contains_form_user_and_anonymous(name, news, have_form):
    """Тест юзера, автора, анонима на наличие формы."""
    url = reverse('news:detail', args=(news.pk,))
    response = name.get(url)
    # Проверяем наличие формы в контексте ответа
    assert ('form' in response.context) == have_form

    # Если форма должна присутствовать, проверяем её тип
    if have_form:
        assert isinstance(response.context['form'], CommentForm)
