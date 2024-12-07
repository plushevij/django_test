from django.urls import reverse

from notes.forms import NoteForm
from .conftest import UniversalTestNote


class TestContent(UniversalTestNote):

    def test_notes_list_for_different_users(self):
        """Тест: разный уровень доступа к заметкам
        для разных пользователей.
        """
        url = reverse('notes:list')
        clients_note_in_list = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for client, note_in_list in clients_note_in_list:
            with self.subTest():
                response = client.get(url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_notes_reader_not_in_list(self):
        """Тест: список заметок не имеет в себе записи
        других пользователей.
        """
        response = self.author_client.get(reverse('notes:list'))
        get_notes = response.context['object_list']
        all_notes = get_notes.count()
        count_of_author_notes = get_notes.filter(author=self.author).count()
        self.assertEqual(all_notes, count_of_author_notes)

    def test_form_in_add_and_edit_pages(self):
        """Тест: Передача формы на страницу добавления заметки."""
        edit_url = reverse('notes:add')
        with self.subTest(name=edit_url):
            response = self.author_client.get(edit_url)
            form = response.context['form']
            self.assertIn('form', response.context)
            self.assertIsInstance(form, NoteForm)
