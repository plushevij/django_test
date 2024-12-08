from http import HTTPStatus

from django.urls import reverse

from .conftest import UniversalTestNote


class TestRoutes(UniversalTestNote):
    """Тесты путей."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.URL_LOGIN = reverse('users:login')
        cls.URL_LOGOUT = reverse('users:logout')
        cls.URL_SINGUP = reverse('users:signup')
        cls.URL_ADD = reverse('notes:add')
        cls.URL_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URL_HOME = reverse('notes:home')
        cls.URL_LIST = reverse('notes:list')
        cls.URL_SUCCESS = reverse('notes:success')

    def test_urls_for_auth_users(self):
        """Тест доступа страниц для авторизованных пользователей."""
        urls = (self.URL_LIST,
                self.URL_ADD,
                self.URL_SUCCESS)
        for url in urls:
            with self.subTest(name=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_anon_users(self):
        """Тест доступа страниц для анонимных пользователей."""
        urls = (self.URL_HOME,
                self.URL_LOGIN,
                self.URL_LOGOUT,
                self.URL_SINGUP)
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Тест доступа только автора к редактированию, удалению и деталям."""
        urls = (self.URL_DETAIL,
                self.URL_EDIT,
                self.URL_DELETE)
        clients_status = (
            (self.reader_client, HTTPStatus.NOT_FOUND),
            (self.author_client, HTTPStatus.OK)
        )
        for url in urls:
            for client, status in clients_status:
                with self.subTest(name=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anon_users(self):
        """Тест редиректов анонимного пользователя"""
        urls = (self.URL_LIST,
                self.URL_ADD,
                self.URL_SUCCESS,
                self.URL_EDIT,
                self.URL_DELETE)
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.URL_LOGIN}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
