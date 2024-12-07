from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .conftest import UniversalTestNote


class TestLogic(UniversalTestNote):
    """Тесты логики работы с заметками."""

    def test_user_can_add_note(self):
        """Аутентифицированный пользователь может создавать заметки."""
        Note.objects.all().delete()
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, self.notes_success_url)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.author)

    def test_anon_cant_add_note(self):
        """Не аутентифицированный пользователь не может создавать заметки."""
        previous_count = Note.objects.count()
        self.client.post(reverse('notes:add'), data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, previous_count)

    def test_if_slug_empty(self):
        """Проверка на пустой слаг."""
        Note.objects.all().delete()
        self.new_form_data.pop('slug')
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertRedirects(response, self.notes_success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditDeleteNote(UniversalTestNote):
    """Тесты редактирования и удаления заметки."""

    def test_author_can_edit(self):
        """Автор может редактировать заметку."""
        response = self.author_client.post(reverse('notes:edit',
                                                   args=(self.note.slug,)),
                                           self.form_data)
        self.assertRedirects(response, self.notes_success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_form_data['title'])
        self.assertEqual(self.note.text, self.new_form_data['text'])
        self.assertEqual(self.note.author, self.author)

    def test_other_users_cant_edit(self):
        """Остальные пользователи не могут редактировать заметку."""
        response = self.reader_client.post(reverse('notes:edit',
                                                   args=(self.note.slug,)),
                                           self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        db_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, db_note.title)
        self.assertEqual(self.note.text, db_note.text)
        self.assertEqual(self.note.slug, db_note.slug)

    def test_author_can_delete(self):
        """Автор может удалить заметку."""
        response = self.author_client.post(reverse('notes:delete',
                                                   args=(self.note.slug,)))
        self.assertRedirects(response, self.notes_success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_users_cant_delete(self):
        """Остальные пользователи не могут удалить заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.reader_client.post(url)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unique_slug(self):
        """Тест на поиск повторяющегося слага."""
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(reverse('notes:add'),
                                           data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)
