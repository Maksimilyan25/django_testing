import pytest

from datetime import datetime, timedelta

from django.test.client import Client


from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Фикстура автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура анонима."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура залогиненного автора."""
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
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
    news_list = []
    today = datetime.today()
    for index in range(11):  # Создаем 11 новостей
        news_item = News.objects.create(
            title=f'Новость {index}',
            text=f'текст {index}',
            date=today - timedelta(days=index)
        )
        news_list.append(news_item)
    return news_list


@pytest.fixture
def create_comments(news, author):
    """Фикстура для создания нескольких комментов."""
    news_list = []
    today = datetime.today()
    for index in range(5):
        comment_item = Comment.objects.create(
            text=f'текст {index}',
            created=today + timedelta(days=index),
            news=news,
            author=author
        )
        news_list.append(comment_item)
    return news_list


@pytest.fixture
def form_data():
    """создание формы."""
    return {
        'text': 'текст'
    }