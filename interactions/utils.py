from rest_framework.pagination import PageNumberPagination

from interactions.models import Recommendation


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
