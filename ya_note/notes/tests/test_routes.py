from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .test_fixtures import BaseTestSetUp


User = get_user_model()


class TestRoutes(BaseTestSetUp):
    """Класс тестирования маршрутов."""

    def test_pages(self):
        """Тест главной страницы и авторизации."""
        for name, url in self.urls.items():
            self.login_author()
            with self.subTest(name=name):
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
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_list_add_done(self):
        """Тест страниц для добавления, списка, успешного добавления."""
        self.login_author()
        for name, url in self.urls.items():
            with self.subTest(name=name):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_user(self):
        """Тест на редирект анонима."""
        login_url = reverse('users:login')
        for name, url in self.urls.items():
            with self.subTest(name=name):
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
