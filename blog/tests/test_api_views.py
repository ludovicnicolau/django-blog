from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from blog.models import BlogPost
from blog import factories

User = get_user_model()

def get_blogger_group():
    content_type = ContentType.objects.get_for_model(BlogPost)
    perm = Permission.objects.get(codename='add_blogpost', content_type=content_type)
    group = Group.objects.create(name='blogger')
    group.permissions.add(perm)
    group.save()
    return group


class BlogPostList(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.random_user = factories.UserFactory()
        cls.blogger_user = factories.UserFactory(groups=(get_blogger_group(),))
        cls.reversed_url = reverse('api-blog:blogpost-list')

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/api/blog/blogposts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_accessible_by_name(self):
        response = self.client.get(self.reversed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_logged_in_cant_create_blogpost(self):
        data = {
            'title': 'The title',
            'content': 'The content',
            'is_published': 'true'
        }
        response = self.client.post(self.reversed_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logged_in_but_no_permission_cant_create_blogpost(self):
        self.client.force_authenticate(user=self.random_user)       
        data = {
            'title': 'The title',
            'content': 'The content',
            'is_published': 'true'
        }
        response = self.client.post(self.reversed_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_can_create_post_with_permission(self):
        self.client.force_authenticate(user=self.blogger_user)
        data = {
            'title': 'The title',
            'content': 'The content',
            'is_published': 'true'
        }
        response = self.client.post(self.reversed_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 1)


class BlogPostDetail(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.random_user = factories.UserFactory()
        blogger_group = get_blogger_group()
        cls.random_blogger = factories.UserFactory(groups=(blogger_group,))
        cls.author = factories.UserFactory(groups=(blogger_group,))
        cls.random_blogpost = factories.BlogPostFactory(author=cls.author, is_published=True)
        cls.url_name = 'api-blog:blogpost-detail'
    
    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(f'/api/blog/blogposts/{self.random_blogpost.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_view_accessible_by_name(self):
        response = self.client.get(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_random_user_cant_partial_update_blogpost(self):
        self.client.force_authenticate(user=self.random_user)
        data = {
            'title': 'New title',
        }
        response = self.client.patch(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_random_user_cant_fully_update_blogpost(self):
        self.client.force_authenticate(user=self.random_user)
        data = {
            'title': 'New title',
            'content': 'New Content',
            'is_published': True,
        }
        response = self.client.put(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_blogger_not_author_cant_partial_update_blogpost(self):
        self.client.force_authenticate(user=self.random_blogger)
        data = {
            'title': 'New title',
        }
        response = self.client.patch(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_blogger_not_author_cant_fully_update_blogpost(self):
        self.client.force_authenticate(user=self.random_blogger)
        data = {
            'title': 'New title',
            'content': 'New Content',
            'is_published': True,
        }
        response = self.client.put(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_author_can_partial_update_blogpost(self):
        self.client.force_authenticate(user=self.author)
        data = {
            'title': 'Partially updated title',
        }
        response = self.client.patch(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_author_can_fully_update_blogpost(self):
        self.client.force_authenticate(user=self.author)
        data = {
            'title': 'Fully updated title',
            'content': 'Fully updated content',
        }
        response = self.client.put(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

class TestBlogPostLikeAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):        
        cls.client = APIClient()
        cls.random_user = factories.UserFactory()
        blogger_group = get_blogger_group()
        cls.random_blogger = factories.UserFactory(groups=(blogger_group,))
        cls.author = factories.UserFactory(groups=(blogger_group,))
        cls.random_blogpost = factories.BlogPostFactory(author=cls.author, is_published=True)
        cls.url_name = 'api-blog:blogpost-like'
    
    def test_authenticated_user_can_like(self):
        self.client.force_authenticate(user=self.random_user)
        self.assertFalse(self.random_blogpost.like_set.filter(user=self.random_user).exists())
        self.assertEqual(self.random_blogpost.like_set.count(), 0)

        response = self.client.post(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(self.random_blogpost.like_set.filter(user=self.random_user).exists())
        self.assertEqual(self.random_blogpost.like_set.count(), 1)

    def test_authenticated_user_can_unlike(self):
        self.client.force_authenticate(user=self.random_user)
        
        self.client.post(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}))
        self.assertEqual(self.random_blogpost.like_set.count(), 1)

        response = self.client.post(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(self.random_blogpost.like_set.filter(user=self.random_user).exists())
        self.assertEqual(self.random_blogpost.like_set.count(), 0)
    
    def test_unauthenticated_cannot_like(self):
        response = self.client.post(reverse(self.url_name, kwargs={'pk': self.random_blogpost.pk}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
