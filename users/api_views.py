from django.db.models import Count

from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import CustomUser
from .serializers import BloggerSerializer
    

class BloggerListAPIView(ListAPIView):
    serializer_class = BloggerSerializer
    queryset = CustomUser.objects.filter(is_active=True, groups__name='bloggers').annotate(blogposts_count=Count('blog_posts'))


class BloggerRetrieveAPIView(RetrieveAPIView):
    serializer_class = BloggerSerializer
    queryset = CustomUser.objects.filter(is_active=True, groups__name='bloggers').annotate(blogposts_count=Count('blog_posts'))
    lookup_field = 'username'
    