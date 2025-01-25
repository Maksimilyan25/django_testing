from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm
from django.utils.text import slugify


User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Фикстура для тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='текст',
            text='куку',
            author=cls.author,
            slug=slugify('Заголовок 1')
        )
        cls.detail_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=[cls.note.pk])

    def test_context_in_list(self):
        """Отдельная заметка попадает на страницу заметок."""
        self.client.force_login(self.author)
        list_url = reverse('notes:list')
        response = self.client.get(list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_other_notes_others_users(self):
        """Чужие заметки не попадают к юзеру."""
        other_author = User.objects.create(username='другой автор')
        other_note = Note.objects.create(
            title='другая заметка',
            text='текст',
            author=other_author,
            slug=slugify('Другая Заметка')
        )
        self.client.force_login(self.author)
        list_url = reverse('notes:list')
        response = self.client.get(list_url)
        self.assertNotIn(other_note, response.context['object_list'])

    def test_anonymous_user_no_form(self):
        """Аноним не получает форму при редактировании и удалении."""
        response = self.client.get(self.detail_url)
        self.assertIsNone(response.context)

    def test_form_pages(self):
        """Тест формы на страницах добавления и редактирования заметок."""
        self.client.force_login(self.author)

        # Проверка страницы добавления заметки
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        # Проверка страницы редактирования заметки
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
