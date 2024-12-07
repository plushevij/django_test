import pytest
from django.conf import settings
from pytest_lazyfixture import lazy_fixture

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, all_news_list, home_url):
    """На главную страницу выпускается 0 новостей."""
    test_news_count.__doc__ = test_news_count.__doc__.format(
        settings.NEWS_COUNT_ON_HOME_PAGE)
    response = client.get(home_url)
    all_news_list = response.context['object_list']
    count_news = all_news_list.count()
    assert count_news == settings.NEWS_COUNT_ON_HOME_PAGE


def test_sorted_news(client, all_news_list, home_url):
    """Сортировка новостей от новейших к старым."""
    response = client.get(home_url)
    all_news_list = response.context['object_list']
    news_dates = [news.date for news in all_news_list]
    assert news_dates == sorted(news_dates, reverse=True)


def test_sorted_comment(client, news_comments, news, detail_url):
    """Сортировка комментариев от новейших к старым."""
    response = client.get(detail_url)
    news = response.context['news']
    news_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in news_comments]
    sorted_timestamps = sorted(all_timestamps, reverse=False)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('client'), False),
        (lazy_fixture('not_author_client'), True)
    ),
)
def test_form_visible(parametrized_client,
                      expected_status,
                      detail_url,
                      not_author_client):
    """Доступ формы комментария для авторизованного пользователя."""
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is expected_status
    if parametrized_client is not_author_client:
        assert isinstance(
            response.context['form'], CommentForm)
