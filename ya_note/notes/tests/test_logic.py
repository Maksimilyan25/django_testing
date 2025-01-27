from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client

from notes.models import Note
from .test_fixtures import BaseTestSetUp

User = get_user_model()


class TestNoteCreate(BaseTestSetUp):
    """Класс теста заметки."""

    NOTE_TEXT = 'текст'

    @classmethod
    def setUpTestData(cls):
        """Данные для БД."""
        super().setUpTestData()
        cls.user = User.objects.create(username='пупс')
        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': 'Обновлённый заголовок'
        }

    def test_anonymous_note(self):
        """Тест, аноним не может создать заметку."""
        # Считаем количество заметок до изменения.
        before_count = Note.objects.count()
        # Выполняем POST запрос для создания заметки.
        self.client.post(self.urls['add'], data=self.form_data)
        # Считаем кол-во заметок после.
        after_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет.
        self.assertEqual(before_count, after_count)

    def test_user_can_create_notes(self):
        """Тест, что юзер может создать заметку."""
        # Чистим БД.
        Note.objects.all().delete()
        # Выполните POST запрос для создания заметки
        response = self.auth_client.post(self.urls['add'], data=self.form_data)
        # Проверяем, что произошла переадресация после создания заметки
        self.assertRedirects(response, self.urls['success'])
        # Теперь проверяем, что заметка была создана
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)  # Ожидается, что будет одна заметка
        # Получаем только что созданную заметку
        note = Note.objects.get()
        # Проверяем, что текст и автор заметки совпадают с ожидаемыми
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.title, self.form_data['title'])


class TestNoteEditDelete(BaseTestSetUp):
    """Класс теста редактирования заметки."""

    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        """Задаем БД."""
        super().setUpTestData()
        # создаем клиент для автора.
        cls.author_client = Client()
        # логиним автора заметки.
        cls.author_client.force_login(cls.author)
        # создаем клиент для читателя.
        cls.reader_client = Client()
        # логиним читателя.
        cls.reader_client.force_login(cls.reader)
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {'text': cls.NEW_NOTE_TEXT, 'title': 'Новый заголовок'}

    def test_author_can_delete_note(self):
        """Тест, что автор заметки может ее удалить."""
        before_count = Note.objects.count()
        response = self.author_client.delete(self.urls['delete'])
        self.assertRedirects(response, self.urls['success'])
        after_count = Note.objects.count()
        self.assertNotEqual(after_count, before_count)

    def test_user_cant_del_note(self):
        """тест, что читатель не может удалить заметку."""
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.urls['delete'])
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что комментарий по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """тест на редактирование заметки."""
        # Получаем заметку по айди.
        note_id = self.notes.id
        self.form_data['text'] = self.NEW_NOTE_TEXT
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(
            self.urls['edit'], data=self.form_data
        )
        # Сохраняем новую заметку.
        updated_note = Note.objects.get(id=note_id)
        self.assertRedirects(response, self.urls['success'])
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.author, self.author)
        self.assertEqual(updated_note.title, self.form_data['title'])

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест, что юзер не может редактировать другие заметки."""
        note_id = self.notes.id
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(
            self.urls['edit'], data=self.form_data
        )
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        updated_note = Note.objects.get(id=note_id)
        # Проверяем, что данные остались тем же, что и были.
        self.assertEqual(updated_note.text, self.NOTE_TEXT)
        self.assertEqual(updated_note.author, self.author)
        self.assertEqual(updated_note.title, self.notes.title)
        self.assertEqual(updated_note.slug, self.notes.slug)
