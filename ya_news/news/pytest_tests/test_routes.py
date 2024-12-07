from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    (
        (lazy_fixture('edit_url')),
        (lazy_fixture('delete_url')),
    ),
)
def test_redirect_for_anon_user_for_edit_delete(client, url, login_url):
    """Тест: Направляется ли анонимынй пользователь
    на страницу login при выборе edit или delete"""
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (lazy_fixture('login_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('logout_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('edit_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('delete_url'), lazy_fixture('author_client'),
         HTTPStatus.OK),
        (lazy_fixture('edit_url'), lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (lazy_fixture('delete_url'), lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (lazy_fixture('home_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('signup_url'), lazy_fixture('client'), HTTPStatus.OK),
        (lazy_fixture('detail_url'), lazy_fixture('client'), HTTPStatus.OK)
    ),
)
def test_redirect_for_author_and_not_author_for_edit_delete(
    url,
    parametrized_client,
    expected_status,
):
    """Тест: Доступ к edit и delete для автора поста,
    и выбрасывание ошибки 404 для другого пользователя"""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
