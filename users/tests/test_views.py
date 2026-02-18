from django.test import TestCase
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from users.models import CustomUser
from blog.models import BlogPost
from blog.factories import UserFactory, BlogPostFactory

import time

def get_blogger_group():
    blogger_group = Group.objects.create(name='bloggers')

    blogpost_content_type = ContentType.objects.get_for_model(BlogPost)
    add_blogpost_permission = Permission.objects.get(codename='add_blogpost', content_type=blogpost_content_type)
    change_blogpost_permission = Permission.objects.get(codename='change_blogpost', content_type=blogpost_content_type)
    delete_blogpost_permission = Permission.objects.get(codename='delete_blogpost', content_type=blogpost_content_type)
    blogger_group.permissions.add(add_blogpost_permission, change_blogpost_permission, delete_blogpost_permission)

    blogger_group.save()

    return blogger_group

class RegisterViewTest(TestCase):

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/users/registration/')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('users:registration'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_created_correctly(self):
        response = self.client.post(reverse('users:registration'), {'username': 'testuser', 'password1': '1h7paJK_KL.', 'password2': '1h7paJK_KL.'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.count(), 1)
    
    def test_correctly_redirected_after_registration(self):
        response = self.client.post(reverse('users:registration'), {'username': 'testuser', 'password1': '1h7paJK_KL.', 'password2': '1h7paJK_KL.'})
        self.assertRedirects(response, reverse('users:registration-success'))


class BloggerListView(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        blogger = CustomUser.objects.create_user(username='Blogger1', password='topsecret')
        blogpost_content_type = ContentType.objects.get_for_model(BlogPost)
        permission = Permission.objects.get(codename='add_blogpost', content_type=blogpost_content_type)
        group = Group.objects.create(name='bloggers')
        group.permissions.add(permission)
        group.save()
        blogger.groups.add(group)
        blogger.save()
        blogger = CustomUser.objects.create_user(username='Blogger2', password='topsecret')
        blogger.groups.add(group)
        blogger.save()
        blogger = CustomUser.objects.create_user(username='Blogger3', password='topsecret', is_active=False)
        blogger.groups.add(group)
        blogger.save()
        CustomUser.objects.create_user(username='Reader', password='topsecret')
    
    def test_view_accessible_at_location(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_use_correct_template(self):
        response = self.client.get(reverse('users:user-list'))
        self.assertTemplateUsed(response, 'users/user_list.html')
    
    def test_show_only_active_bloggers(self):
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(len(response.context['users']), 2)


class BloggerDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        blogger_group = get_blogger_group()

        cls.active_author = UserFactory(groups=(blogger_group,))

        cls.inactive_author = UserFactory(groups=(blogger_group,), is_active=False)
        cls.reader = UserFactory()

        BlogPostFactory.create_batch(7, author=cls.active_author, is_published=True)
        BlogPostFactory.create_batch(2, author=cls.active_author, is_published=False)
    
    def test_view_url_exist_at_desired_location(self):
        # user = CustomUser.objects.get(username__exact='Author')
        # response = self.client.get(f'/users/profile/{user.username}/')
        response = self.client.get(f'/users/profile/{self.active_author.username}/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        # user = CustomUser.objects.get(username__exact='Author')
        # response = self.client.get(reverse('users:user-detail', kwargs={'username': user.username}))
        response = self.client.get(reverse('users:user-detail', kwargs={'username': self.active_author.username}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_display_only_published_posts(self):
        # user = CustomUser.objects.get(username__exact='Author')
        # response = self.client.get(user.get_absolute_url())
        response = self.client.get(self.active_author.get_absolute_url())
        # number_of_posts = user.blog_posts.count()
        number_of_posts = response.context['profile_user'].blog_posts.count()
        self.assertEqual(number_of_posts, 7)
    
    def test_view_use_the_correct_template(self):        
        # user = CustomUser.objects.get(username__exact='Author')
        # response = self.client.get(user.get_absolute_url())
        response = self.client.get(self.active_author.get_absolute_url())
        self.assertTemplateUsed(response, 'users/user_detail.html')

    def test_view_404_if_blogger_not_active(self):
        # user = CustomUser.objects.get(username='Author2')
        # response = self.client.get(reverse('users:user-detail', kwargs={'username': user.username})) # Can't use user.get_absolute_url() for the test, because it returns the delete user view
        response = self.client.get(reverse('users:user-detail', kwargs={'username': self.inactive_author.username})) # Can't use user.get_absolute_url() for the test, because it returns the delete user view
        self.assertEqual(response.status_code, 404)


class BloggerDeleteViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_view_accessible_at_url(self):
        self.client.force_login(user=self.user)
        response = self.client.get(f'/users/user-delete/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('users:user-delete'))
        self.assertEqual(response.status_code, 200)

    def test_not_logged_in_cannot_access(self):
        response = self.client.get(reverse('users:user-delete'))
        self.assertEqual(response.status_code, 302)

    def test_user_logged_out_after_deletion(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('users:user-delete'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_deleted_user_still_in_db_with_is_active_false(self):
        self.client.force_login(user=self.user)
        response = self.client.post(reverse('users:user-delete'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertFalse(CustomUser.objects.get(username=self.user.username).is_active)


class BiographyUpdateViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory(biography='')
        self.url = reverse('users:biography-update')

    def test_view_accessible_at_location(self):
        self.client.force_login(user=self.user)
        response = self.client.get('/users/biography-update/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        self.client.force_login(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_success_redirected_to_user_profile(self):
        self.client.force_login(user=self.user)
        response = self.client.post(self.url, data={'biography': 'new'})
        self.assertRedirects(response, self.user.get_absolute_url())
    
    def test_biography_updated(self):
        self.client.force_login(user=self.user)
        response = self.client.post(self.url, data={'biography': 'new'})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db(fields=('biography',))
        self.assertEqual('new', self.user.biography)