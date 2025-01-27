from http import HTTPStatus

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm

import pytest


pytestmark = pytest.mark.django_db


def test_pages_paginator(client, all_routes, create_news):
    """Тест количества новостей на странице."""
    url = reverse(all_routes[0])
    response = client.get(url)
    news_count = len(response.context['object_list'])
    assert response.status_code == HTTPStatus.OK
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_order_news_on_page(client, all_routes, create_news):
    """Тест, сортировка новостей по убыванию."""
    url = reverse(all_routes[0])
    response = client.get(url)
    all_dates = [news.date for news in response.context['object_list']]
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
