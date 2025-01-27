from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.models import Note


class BaseTestSetUp(TestCase):
    """Базовая фикстура для всех тестов."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестов."""
        cls.author = User.objects.create(username='Автор')  # автор
        cls.reader = User.objects.create(username='Читатель')  # пользователь
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст комментария',
            author=cls.author,
            slug=slugify('Заголовок')
        )
        cls.urls = {
            'list': reverse('notes:list'),
            'add': reverse('notes:add'),
            'success': reverse('notes:success'),
            'detail': reverse('notes:detail', args=(cls.notes.slug,)),
            'edit': reverse('notes:edit', args=(cls.notes.slug,)),
            'delete': reverse('notes:delete', args=(cls.notes.slug,)),
        }

    def login_author(self):
        """Логин автора для прохода тестов."""
        self.client.force_login(self.author)
