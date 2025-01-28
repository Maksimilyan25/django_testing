from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .test_fixtures import BaseTestSetUp


User = get_user_model()


class TestRoutes(BaseTestSetUp):
    """Класс тестирования маршрутов."""

    def test_pages(self):
        """Тест главной страницы и авторизации."""
        for url in self.auth_and_home_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_edit_and_delete(self):
        """Тест страницы редактирования и удаления."""
        users_status = (
            (self.author_client, HTTPStatus.OK),
            (self.user_client, HTTPStatus.NOT_FOUND),
        )
        for client, status in users_status:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(client=client, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_list_add_done(self):
        """Тест страниц для добавления, списка, успешного добавления."""
        for name, url in self.urls.items():
            with self.subTest(name=name):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymous_user(self):
        """Тест на редирект анонима."""
        login_url = self.auth_and_home_urls[1]
        for name, url in self.urls.items():
            with self.subTest(name=name):
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
