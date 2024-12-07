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
            'slug': 'Новый слаг'
        }
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)


class UniversalTestNote(UniversalTestClass):
    """Универсальный класс тестов для заметок."""
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст',
            author=cls.author,
        )
        # cls.add_url = reverse('notes:add')
        # cls.edit_url = reverse(
        #     'notes:edit',
        #     kwargs={'slug': cls.note.slug})
        # cls.add_and_edit_urls = (cls.add_url, cls.edit_url)
