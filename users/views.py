from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.db.models.aggregates import Count
from django.db.models import Q, Prefetch
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth import logout

from .forms import RegisterForm, BiographyUpdateForm
from .models import CustomUser
from blog.models import BlogPost


def deleted_profile(request):
    return render(request, 'users/deleted_profile.html', {})


class RegisterView(CreateView):
    form_class = RegisterForm
    model = CustomUser
    success_url = reverse_lazy('users:registration-success')


def registration_success(request):
    return render(request, 'users/registration_success.html', {})


class BiographyUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = BiographyUpdateForm
    template_name = 'users/biography_form.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class BloggerListView(ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.filter(groups__name__exact='bloggers', is_active=True).annotate(blogpost_count=Count('blog_posts', filter=Q(blog_posts__is_published=True)))


class BloggerDetailView(DetailView):
    model = CustomUser
    context_object_name = 'profile_user'
    template_name = 'users/user_detail.html'
    pk_url_kwarg = 'username'

    def get_queryset(self):
        queryset = CustomUser.objects.filter(is_active=True)
        # if self.request.user.is_authenticated and self.request.user.pk == self.kwargs['pk']:
        if self.request.user.is_authenticated and self.request.user.username == self.kwargs['username']:
            queryset = queryset.prefetch_related(Prefetch('blog_posts', BlogPost.objects.annotate(likes_count=Count('like')).order_by('-last_edited_date')))
        else:
            queryset = queryset.prefetch_related(Prefetch('blog_posts', BlogPost.objects.filter(is_published=True).annotate(likes_count=Count('like')).order_by('-last_edited_date')))
        return queryset

    def get_object(self):
        return get_object_or_404(self.get_queryset(), username=self.kwargs['username'], is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object
        user_is_author = self.request.user.id == author.id
        context['user_is_author'] = user_is_author
        context['profile_user_is_a_blogger'] = author.has_perm('blog.add_blogpost')
        
        return context


def deletion_success(request):
    return render(request, 'users/deletion_success.html', {})


class BloggerDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy('users:deletion-success')
    
    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        self.object.is_active = False
        self.object.save()
        logout(self.request)
        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)