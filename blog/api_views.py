from django.db.models import Count, F

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework import filters

from .models import BlogPost, Comment
from .permissions import IsABloggerPermission, IsAdminOrOwner
from .serializers import BlogPostSerializer, CommentSerializer, LikeSerializer


class BlogPostAPIViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = (AllowAny,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content',]
    ordering = ['-published_date',]
    ordering_fields = ['published_date', 'title', 'likes_count']
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        queryset = self.queryset.annotate(likes_count=Count('like')).order_by('-published_date').select_related('author')
        author_username = self.request.GET.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username, author__is_active=True) # If the author has deleted his account, we do not show any of his blog posts
        if self.request.user.username != author_username: # No problem since CustomUser.username is unique
            queryset = queryset.filter(is_published=True)
        return queryset

    def get_permissions(self):
        if self.action == 'comments':
            if self.request.method == 'POST':
                self.permission_classes = (IsAuthenticated,)
            elif self.request.method == 'GET':
                self.permission_classes = (AllowAny,)
        elif self.action == 'toggle_like':
            if self.request.method == 'POST':
                self.permission_classes = (IsAuthenticated,)
        elif self.action in ('update', 'partial_update', 'destroy'):
            self.permission_classes = (IsAdminOrOwner,)
        else:
            self.permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('get', 'post'), detail=True, url_path='comments', url_name='blogpost-comments', serializer_class=CommentSerializer)
    def comments(self, request, slug=None):
        blog_post = self.get_object()
        if request.method == 'GET':
            queryset = blog_post.comments.all()
            serializer = CommentSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user, blog_post=blog_post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(methods=('get', 'post',), permission_classes=(IsAuthenticated,), detail=True, url_path='like', url_name='like', serializer_class=LikeSerializer)
    def toggle_like(self, request, slug=None):
        if request.method == 'GET':
            return Response(status=status.HTTP_200_OK)

        if request.method == 'POST':
            blog_post = self.get_object()

            like, created = blog_post.like_set.get_or_create(user=request.user, blog_post=blog_post)
            if not created:
                like.delete()

        return Response({'likes_count': blog_post.like_set.count()}, status=status.HTTP_200_OK)

            