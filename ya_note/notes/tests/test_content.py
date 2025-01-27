from django.contrib.auth import get_user_model
from django.utils.text import slugify

from notes.models import Note
from notes.forms import NoteForm
from .test_fixtures import BaseTestSetUp


User = get_user_model()


class TestHomePage(BaseTestSetUp):
    """Класс тестов контента."""

    @classmethod
    def setUpTestData(cls):
        """Вызов родительского и переопределение."""
        super().setUpTestData()
        cls.other_author = User.objects.create(username='другой автор')
        cls.other_note = Note.objects.create(
            title='другая заметка',
            text='текст',
            author=cls.other_author,
            slug=slugify('Другая Заметка')
        )

    def test_context_in_list(self):
        """Отдельная заметка попадает на страницу заметок."""
        self.login_author()
        response = self.client.get(self.urls['list'])
        self.assertIn(self.notes, response.context['object_list'])

    def test_other_notes_others_users(self):
        """Чужие заметки не попадают к юзеру."""
        self.login_author()
        response = self.client.get(self.urls['list'])
        self.assertNotIn(self.other_note, response.context['object_list'])

    def test_anonymous_user_no_form(self):
        """Аноним не получает форму при редактировании и удалении."""
        response = self.client.get(self.urls['add'])
        self.assertIsNone(response.context)

    def test_form_pages(self):
        """Тест формы на страницах добавления и редактирования заметок."""
        self.client.force_login(self.author)

        # Проверка страницы добавления заметки
        response = self.client.get(self.urls['add'])
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        # Проверка страницы редактирования заметки
        response = self.client.get(self.urls['edit'])
        with self.subTest('Проверка наличия формы'):
            self.assertIn('form', response.context, 'Форма не найдена.')

        with self.subTest('Проверка типа формы'):
            self.assertIsInstance(
                response.context['form'],
                NoteForm,
                'Форма не является экземпляром NoteForm.'
            )
