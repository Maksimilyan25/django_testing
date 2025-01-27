from http import HTTPStatus

from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура пользователя."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура залогиненного автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура залогиненного юзера."""
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(author):
    """Фикстура новости."""
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(news, author):
    """Фикстура коммента."""
    comment = Comment.objects.create(
        text='текст',
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def create_news(db):
    """Фикстура для создания нескольких новостей."""
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'Новость {index}',
            text=f'текст {index}',
            date=today - timedelta(days=index)
        )


@pytest.fixture
def create_comments(news, author):
    """Фикстура для создания нескольких комментов."""
    today = datetime.today()
    for index in range(5):
        Comment.objects.create(
            text=f'текст {index}',
            news=news,
            author=author
        )
        comment.created = today + timedelta(days=index)


@pytest.fixture
def all_routes():
    """Фикстура всех адресов."""
    return [
        'news:home',
        'news:detail',
        'news:edit',
        'news:delete',
        'users:login',
        'users:logout',
        'users:signup'
    ]


@pytest.fixture
def anonymous_routes(client):
    """Адреса для анонима."""
    return (
        ('news:home', client, HTTPStatus.OK),
        ('users:login', client, HTTPStatus.OK),
        ('users:logout', client, HTTPStatus.OK),
        ('users:signup', client, HTTPStatus.OK),
        ('news:detail', client, HTTPStatus.OK),
    )


@pytest.fixture
def client_routes(author_client, not_author_client):
    """Адреса для клиента."""
    """Фикстура для маршрутов, клиентов и ожидаемых статусов."""
    return (
        ('news:edit', author_client, HTTPStatus.OK),
        ('news:delete', author_client, HTTPStatus.OK),
        ('news:edit', not_author_client, HTTPStatus.NOT_FOUND),
        ('news:delete', not_author_client, HTTPStatus.NOT_FOUND),
    )
