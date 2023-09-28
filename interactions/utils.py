from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from interactions.models import Recommendation, Bookmark


class CommentsPagination(PageNumberPagination):
    page_size = 20


class UserLikeListPagination(PageNumberPagination):
    page_size = 20


def recommendation_counter(user, categories, flag=False):
    for category in categories:
        recommendation_obj, created = Recommendation.objects.get_or_create(user=user, category=category)
        if flag:
            recommendation_obj.count += 1
        else:
            recommendation_obj.count -= 1

        recommendation_obj.save()


def bookmark_operator(action, bookmark_query, user, item):
    response_status = status.HTTP_200_OK
    state = "success"
    if action == "unsave" and bookmark_query.exists():
        bookmark_query.delete()
        message = "Bookmark Deleted"

    elif action == "save" and not bookmark_query.exists():
        Bookmark.objects.create(user=user, content_object=item)
        message = "Bookmark Done"

    else:
        state = "error"
        message = "Action Undetected"
        response_status = status.HTTP_400_BAD_REQUEST

    return state, message, response_status
