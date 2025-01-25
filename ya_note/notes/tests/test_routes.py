from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Класс тестирования маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестов."""
        cls.author = User.objects.create(username='Васька')  # автор
        cls.reader = User.objects.create(username='Ноунейм')  # пользователь
        cls.notes = Note.objects.create(
            # фикстура заметки.
            title='Заголовок 1',
            text='Текст 1',
            author=cls.author,
            slug=slugify('Заголовок 1')
        )

    def test_pages(self):
        """Тест главной страницы и авторизации."""
        urls = (
            ('notes:home', None),
            ('notes:detail', self.notes.slug),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_edit_and_delete(self):
        """Тест страницы редактирования и удаления."""
        users_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_status:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_list_add_done(self):
        """Тест страниц для добавления, списка, успешного добавления."""
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_user(self):
        """Тест на редирект анонима."""
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', self.notes.slug),
            ('notes:edit', self.notes.slug),
            ('notes:delete', self.notes.slug),
        )
        login_url = reverse('users:login')

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
