from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


pytestmark = pytest.mark.django_db


COMMENT_DATA = {
    'titlet': 'новый комментарий',
    'text': 'текст комментария',
}


def test_anon_is_not_post_comment(client, detail_url, login_url):
    """Тест: Анонимный пользователь не может отправить коммент."""
    old_comments = Comment.objects.count()
    response = client.post(detail_url, data=COMMENT_DATA)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == old_comments


def test_auth_user_post_comment(not_author_client, not_author,
                                news, detail_url):
    """Тест: Авторизованный пользователь может отправить коммент."""
    Comment.objects.all().delete()
    response = not_author_client.post(detail_url, data=COMMENT_DATA)
    assertRedirects(response, detail_url + '#comments')
    new_comment = Comment.objects.get()
    assert Comment.objects.count() == 1
    assert new_comment.text == COMMENT_DATA['text']
    assert new_comment.author == not_author
    assert new_comment.news == news


def test_auth_user_edit_comment(author_client, comment,
                                edit_url, detail_url):
    """Тест: Авторизованный пользователь может
    отредактировать комментарий.
    """
    response = author_client.post(edit_url, data=COMMENT_DATA)
    update_comment = Comment.objects.get(id=comment.id)
    assertRedirects(response, detail_url + '#comments')
    assert update_comment.text == COMMENT_DATA['text']
    assert comment.author == update_comment.author
    assert comment.news == update_comment.news


def test_auth_user_delete_comment(author_client, delete_url, detail_url):
    """Тест: Авторизованный пользователь может
    удалить комментарий.
    """
    all_comments = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, detail_url + '#comments')
    assert Comment.objects.count() == all_comments - 1


def test_not_author_edit_comment(not_author_client, comment, edit_url):
    """Тест: Авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    response = not_author_client.post(edit_url, data=COMMENT_DATA)
    update_comment = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert update_comment.text == comment.text
    assert update_comment.author == comment.author
    assert update_comment.news == comment.news


def test_not_author_delete_comment(not_author_client, delete_url):
    """Тест: Авторизованный пользователь не может
    удалять чужие комментарии.
    """
    old_comments = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == old_comments


def test_bad_words(author_client, detail_url):
    """Комментарии с плохими словами не будут
    опубликованы, форма вернет предупреждение и оишбку.
    """
    old_comment = Comment.objects.count()
    COMMENT_DATA['text'] = f'Текст со словом {BAD_WORDS[0]}'
    response = author_client.post(detail_url, data=COMMENT_DATA)
    assert Comment.objects.count() == old_comment
    assertFormError(response, form='form', field='text', errors=WARNING)
