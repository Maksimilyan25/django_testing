from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.text import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreate(TestCase):
    """Класс теста заметки."""

    NOTE_TEXT = 'текст'

    @classmethod
    def setUpTestData(cls):
        """Данные для БД."""
        cls.author = User.objects.create(username='пупсик')
        # Адрес страницы с заметкой.
        cls.url = reverse('notes:add')
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
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом заметки.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_notes(self):
        """Тест, что юзер может создать заметку."""
        # Выполните POST запрос для создания заметки
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что произошла переадресация после создания заметки
        self.assertRedirects(response, reverse('notes:success'))
        # Теперь проверяем, что заметка была создана
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)  # Ожидается, что будет одна заметка
        # Получаем только что созданную заметку
        note = Note.objects.get()
        # Проверяем, что текст и автор заметки совпадают с ожидаемыми
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    """Класс теста редактирования заметки."""

    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        """Задаем БД."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        # создаем заметку.
        cls.note = Note.objects.create(
            title='текст',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=slugify('Заголовок 1')
        )
        # получаем адрес заметки.
        note_url = reverse('notes:detail', args=(cls.note.slug,))
        # создаем клиент для автора.
        cls.author_client = Client()
        # логиним автора заметки.
        cls.author_client.force_login(cls.author)
        # создаем клиент для читателя.
        cls.reader_client = Client()
        # логиним читателя.
        cls.reader_client.force_login(cls.reader)
        # URL для редактирования заметки.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления заметки.
        cls.del_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению заметки.
        cls.form_data = {'text': cls.NOTE_TEXT, 'title': 'Новый заголовок'}

    def test_author_can_delete_note(self):
        """Тест, что автор заметки может ее удалить."""
        # От имени автора заметки отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.del_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, reverse('notes:success'))
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)

    def test_user_cant_del_note(self):
        """тест, что читатель не может удалить заметку."""
        # Выполняем запрос на удаление от пользователя-читателя.
        response = self.reader_client.delete(self.del_url)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что комментарий по-прежнему на месте.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """тест на редактирование заметки."""
        self.form_data['text'] = self.NEW_NOTE_TEXT
        # Выполняем запрос на редактирование от имени автора комментария.
        response = self.author_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что сработал редирект.
        self.assertRedirects(response, reverse('notes:success'))
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест, что юзер не может редактировать другие заметки."""
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.NOTE_TEXT)
