from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.db.models import Count, Q, When, Case, F
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.db.models import FloatField, Prefetch
from django.core.paginator import Paginator

from .forms import BlogPostForm, CommentForm
from .models import BlogPost, Comment, Category


def home(request):
    return render(request, 'blog/home.html', {})


class BlogPostListView(ListView):
    model = BlogPost
    context_object_name = 'blog_posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True).select_related('author').annotate(likes_count=Count('likes'))
        
        order_by = self.request.GET.get('order_by')
        order_by_field = '-last_edited_date'
        if order_by == 'date-asc':
            order_by_field = 'last_edited_date'
        elif order_by == 'like-desc':
            order_by_field = '-likes_count'
        elif order_by == 'like-asc':
            order_by_field = 'likes_count'
        elif order_by == 'view-asc':
            order_by_field = 'view_count'
        elif order_by == 'view-desc':
            order_by_field = '-view_count'
        else:
            order_by_field = '-last_edited_date'
        
        queryset = queryset.order_by(order_by_field)

        search = self.request.GET.get('search')
        if search:
            queryset = (
                queryset
                .filter(Q(title__icontains=search) | Q(content__icontains=search))
                .annotate(relevance=Case(
                    When(title__icontains=search, then=1),
                    default=0.5,
                    output_field=FloatField()
                ))
                .order_by('-relevance', order_by_field)
            )

        return queryset


class BlogPostDetailView(DetailView):
    model = BlogPost
    context_object_name = 'blog_post'

    def get_queryset(self):
        return BlogPost.objects.select_related('author').prefetch_related('comments__author').annotate(likes_count=Count('likes'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        blogpost = self.object
        
        if blogpost.author != self.request.user:
            BlogPost.objects.filter(pk=self.kwargs['pk']).update(view_count=F('view_count') + 1)

        if self.request.user.is_authenticated:
            context['user_liked'] = blogpost.like_set.filter(user=self.request.user).exists()
        else:
            context['user_liked'] = False        
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    
    def get_success_url(self):
        return reverse('blog:blog-detail', kwargs={'pk': self.object.blog_post.pk}, fragment='comments')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_post'] = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog_post = get_object_or_404(BlogPost, pk=self.kwargs['pk'])
        form.save()
        return super().form_valid(form)


class BlogPostCreateView(PermissionRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    permission_required = ('blog.add_blogpost',)

    def get_success_url(self):
        return reverse('blog:blog-detail', kwargs={'pk': self.object.pk,})
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()    
        return super().form_valid(form)


class BlogPostUpdateView(PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    permission_required = ('blog.change_blogpost',)

    def get_success_url(self):
        return reverse('blog:blog-detail', kwargs={'pk': self.object.pk,})
    
    def test_func(self):
        return self.get_object().author == self.request.user


class BlogPostDeleteView(PermissionRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    permission_required = ('blog.delete_blogpost',)

    def get_success_url(self):
        if self.request.GET.get('next'):
            return self.request.GET.get('next')
        return self.request.user.get_absolute_url()

    def test_func(self):
        return self.get_object().author == self.request.user


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category_detail.html'
    context_object_name = 'category'
    queryset = Category.objects.all().prefetch_related(Prefetch('blogposts', BlogPost.objects.filter(is_published=True)), 'blogposts__author')

    def get_object(self):
        category = get_object_or_404(self.get_queryset(), name=self.kwargs['name'])
        return category
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.object.blogposts.all(), 9)
        context['paginator'] = paginator
        if paginator.num_pages > 1:
            context['is_paginated'] = True
        else:
            context['is_paginated'] = False
        page = self.request.GET.get('page') 
        if page is None:
            page = 1
        context['page_obj'] = paginator.page(page)
        context['blogposts'] = paginator.get_page(page)
        return context