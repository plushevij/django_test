from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class UniversalTestClass(TestCase):
    """Универсальный класс тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
        }
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes_success_url = reverse('notes:success')
        cls.new_form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'Новый слаг'
        }


class UniversalTestNote(UniversalTestClass):
    """Универсальный класс тестов для заметок."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Новый заголовок',
            text='Новый текст',
            author=cls.author,
            slug='slug'
        )
