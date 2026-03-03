from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from blog.models import BlogPost, Comment, Category
from blog.factories import BlogPostFactory, UserFactory

import time

User = get_user_model()

def get_blogger_group():
    content_type = ContentType.objects.get_for_model(BlogPost)
    add_blogpost_perm = Permission.objects.get(codename='add_blogpost', content_type=content_type)
    delete_blogpost_perm = Permission.objects.get(codename='delete_blogpost', content_type=content_type)
    change_blogpost_perm = Permission.objects.get(codename='change_blogpost', content_type=content_type)
    blogger_group = Group.objects.create(name='blogger')
    blogger_group.permissions.add(add_blogpost_perm, delete_blogpost_perm, change_blogpost_perm)
    blogger_group.save()
    return blogger_group


class HomeViewTest(TestCase):

    def test_root_redirect_to_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 301)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('blog:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_use_correct_template(self):
        response = self.client.get(reverse('blog:home'))
        self.assertTemplateUsed(response, 'blog/home.html')


class BlogPostDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Author', password='topsecret')
        user = User.objects.create_user(username='Random', password='topsecret')
        cls.blogpost = BlogPost.objects.create(title='The title.', content='The content', author=cls.author, is_published=True)
        Comment.objects.create(text='A first comment.', author=user, blog_post=cls.blogpost)
        time.sleep(0.1)
        Comment.objects.create(text='A second comment.', author=user, blog_post=cls.blogpost)
    
    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(f'/blog/{self.blogpost.slug}/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('blog:blog-detail', kwargs={'slug': self.blogpost.slug}))
        self.assertEqual(response.status_code, 200)

    def test_use_the_correct_template(self):
        response = self.client.get(self.blogpost.get_absolute_url())
        self.assertTemplateUsed(response, 'blog/blogpost_detail.html')
    
    def test_blog_post_name_in_context(self):
        response = self.client.get(self.blogpost.get_absolute_url())
        self.assertTrue('blog_post' in response.context)
    
    def test_comments_are_displayed_from_oldest_to_most_recent(self):
        response = self.client.get(self.blogpost.get_absolute_url())
        self.assertLess(response.context['blog_post'].comments.all()[0].last_edited_date, response.context['blog_post'].comments.all()[1].last_edited_date)

    def test_views_do_not_increase_if_viewer_is_author(self):
        self.blogpost.refresh_from_db(fields=('view_count',))
        current_views = self.blogpost.view_count
        self.client.force_login(user=self.author) 
        response = self.client.get(self.blogpost.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.blogpost.refresh_from_db(fields=('view_count',))
        self.assertEqual(current_views, self.blogpost.view_count)

    def test_views_increase_if_published(self):
        self.blogpost.refresh_from_db(fields=('view_count',))
        current_views = self.blogpost.view_count
        response = self.client.get(self.blogpost.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.blogpost.refresh_from_db(fields=('view_count',))
        self.assertEqual(self.blogpost.view_count, current_views+1)
        


class BlogPostListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        blogger_group = get_blogger_group()
        author = UserFactory(groups=(blogger_group,))
        BlogPostFactory.create_batch(17, is_published=True, author=author)
        BlogPostFactory(is_published=False, author=author)
    
    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/blog/blogs/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertEqual(response.status_code, 200)
    
    def test_blog_posts_name_in_context(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertTrue('blog_posts' in response.context)
    
    def test_blog_posts_most_recent_first(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertGreater(response.context['blog_posts'][0].last_edited_date, response.context['blog_posts'][1].last_edited_date)
    
    def test_use_the_correct_template(self):
        response = self.client.get(reverse('blog:blogs'))
        self.assertTemplateUsed(response, 'blog/blogpost_list.html')

    def test_paginated_by_9_and_display_only_published(self):
        response = self.client.get(reverse('blog:blogs'))
        number_of_blogs = len(response.context['blog_posts'])
        self.assertEqual(number_of_blogs, 9)
        page_obj = response.context['page_obj']
        next_page_url = reverse('blog:blogs') + f'?page={page_obj.next_page_number()}'
        response = self.client.get(next_page_url)
        number_of_blogs = len(response.context['blog_posts'])
        self.assertEqual(number_of_blogs, 8)


class CommentCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        blogger_group = get_blogger_group()
        cls.author = UserFactory(groups=(blogger_group,))
        cls.reader = UserFactory()
        cls.blogpost = BlogPostFactory(author=cls.author)

    def test_view_url_exist_at_desired_location_if_logged_in(self):
        self.client.force_login(user=self.reader)
        response = self.client.get(f'/blog/{self.blogpost.slug}/create/')
        self.assertEqual(response.status_code, 200)

    def test_view_redirected_to_login_if_logged_out(self):
        url = reverse('blog:comment-form', kwargs={'slug': self.blogpost.slug})
        response = self.client.get(url)
        next = f'?next={url}'
        self.assertRedirects(response, reverse('users:login') + next)

    def test_view_accessible_by_name(self):
        self.client.force_login(user=self.reader)
        response = self.client.get(reverse('blog:comment-form', kwargs={'slug': self.blogpost.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_use_the_correct_template(self):
        self.client.force_login(user=self.reader)
        response = self.client.get(reverse('blog:comment-form', kwargs={'slug': self.blogpost.slug}))
        self.assertTemplateUsed(response, 'blog/comment_form.html')

    def test_redirect_on_correct_url_on_success(self):
        self.client.force_login(user=self.reader)
        response = self.client.post(reverse('blog:comment-form', kwargs={'slug': self.blogpost.slug}), data={'text': 'A great comment.'})
        self.assertRedirects(response, reverse('blog:blog-detail', kwargs={'slug': self.blogpost.slug}, fragment='comments'))


class BlogPostCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        blogger = User.objects.create_user(username='Blogger', password='topsecret')
        permission = Permission.objects.get(name='Can add Blog Post')
        blogger.user_permissions.add(permission)
        User.objects.create_user(username='Reader', password='topsecret')
        cls.category = Category.objects.create(name='movies')

    def test_view_accessible_at_location_if_has_permission(self):
        login = self.client.login(username='Blogger', password='topsecret')
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name_if_has_permission(self):
        login = self.client.login(username='Blogger', password='topsecret')
        response = self.client.get(reverse('blog:blog-create'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_forbidden_if_no_permission(self):
        login = self.client.login(username='Reader', password='topsecret')
        response = self.client.get(reverse('blog:blog-create'))
        self.assertEqual(response.status_code, 403)

    def test_redirect_to_correct_url(self):
        login = self.client.login(username='Blogger', password='topsecret')
        response = self.client.post(
            reverse('blog:blog-create'),
            data={
                'title': 'The title',
                'content': 'The content.',
                'categories': [self.category.pk,],
            }
        )
        blog_post = BlogPost.objects.get(title__exact='The title')
        self.assertRedirects(response, reverse('blog:blog-detail', kwargs={'slug': blog_post.slug}))
    
    def test_author_is_correct_on_created_blog_post(self):        
        login = self.client.login(username='Blogger', password='topsecret')
        response = self.client.post(
            reverse('blog:blog-create'),
            data={
                'title': 'The title', 
                'content': 'The content.',
                'categories': [self.category.pk,],
            }
        )
        blog_post = BlogPost.objects.get(title__exact='The title')
        blogger = User.objects.get(username__exact='Blogger')
        self.assertEqual(blogger.pk, blog_post.author.pk)


class BlogPostUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        blogpost_contenttype = ContentType.objects.get_for_model(BlogPost)
        permission = Permission.objects.get(codename='change_blogpost', content_type=blogpost_contenttype)
        blogger1 = User.objects.create_user(username='Blogger1', password='topsecret')
        blogger1.user_permissions.add(permission)
        blogger2 = User.objects.create_user(username='Blogger2', password='topsecret')
        blogger2.user_permissions.add(permission)
        reader = User.objects.create_user(username='Reader', password='topsecret')
        cls.category = Category.objects.create(name='movies')
        BlogPost.objects.create(title='The title.', content='The content.', author=blogger1)
    
    def test_view_accessible_at_location(self):
        blogpost = BlogPost.objects.get(title__exact='The title.')
        login = self.client.login(username='Blogger1', password='topsecret')
        response = self.client.get(f'/blog/{blogpost.slug}/update/')
        self.assertEqual(response.status_code, 200)

    def test_view_accessible_by_name(self):
        blogpost = BlogPost.objects.get(title__exact='The title.')
        login = self.client.login(username='Blogger1', password='topsecret')
        response = self.client.get(reverse('blog:blog-update', kwargs={'slug': blogpost.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_forbidden_if_no_permission(self):
        blogpost = BlogPost.objects.get(title__exact='The title.')
        login = self.client.login(username='Reader', password='topsecret')
        response = self.client.get(reverse('blog:blog-update', kwargs={'slug': blogpost.slug}))
        self.assertEqual(response.status_code, 403)        

    def test_view_forbidden_if_not_the_author(self):
        blogpost = BlogPost.objects.get(title__exact='The title.')
        login = self.client.login(username='Blogger2', password='topsecret')
        response = self.client.get(reverse('blog:blog-update', kwargs={'slug': blogpost.slug}))
        self.assertEqual(response.status_code, 403)

    def test_correctly_redirected_after_update(self):
        author = User.objects.get(username='Blogger1')
        blogpost = BlogPost.objects.create(title='A random title', content='A random content', is_published=True, author=author)
        login = self.client.login(username='Blogger1', password='topsecret')
        response = self.client.get(reverse('blog:blog-update', kwargs={'slug': blogpost.slug}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('blog:blog-update', kwargs={'slug': blogpost.slug}), 
            data={
                'title': 'The new title.', 
                'content': 'A random content', 
                'is_published': True,
                'categories': [self.category.pk,],
            }
        )
        self.assertRedirects(response, reverse('blog:blog-detail', kwargs={'slug': blogpost.slug}))


class TestBlogPostDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):        
        blogger_group = get_blogger_group()
        cls.blogger = UserFactory(groups=(blogger_group,))
        cls.blogger_not_author = UserFactory(groups=(blogger_group,))
        cls.random_user = UserFactory()

    def setUp(self):
        self.blogpost = BlogPostFactory(author=self.blogger)
    
    def test_not_allowed_cannot_delete(self):
        """
        Only users logged in with the blog.delete_blogpost permission can post on this view.
        """
        self.client.force_login(user=self.random_user)
        response = self.client.post(reverse('blog:blog-delete', kwargs={'slug': self.blogpost.slug}), data={})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(BlogPost.objects.count(), 1)
    
    def test_blogger_not_author_cannot_delete(self):
        self.client.force_login(user=self.blogger_not_author)
        response = self.client.post(reverse('blog:blog-delete', kwargs={'slug': self.blogpost.slug}), data={})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(BlogPost.objects.count(), 1)
    
    def test_author_can_delete(self):
        self.client.force_login(user=self.blogger)
        response = self.client.post(reverse('blog:blog-delete', kwargs={'slug': self.blogpost.slug}), data={})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BlogPost.objects.count(), 0)


class TestCategoryListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='movies')
    
    def test_view_accessible_at_location(self):
        response = self.client.get('/blog/categories/')
        self.assertEqual(response.status_code, 200)

    def test_accessible_by_name(self):
        response = self.client.get(reverse('blog:category-list'))
        self.assertEqual(response.status_code, 200)
    
    def test_use_correct_template(self):
        response = self.client.get(reverse('blog:category-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_list.html')
    
    def test_context_object_name_is_categories(self):
        response = self.client.get(reverse('blog:category-list'))
        self.assertEqual(response.status_code, 200)
        expected_context_object_name = 'categories'
        self.assertIn(expected_context_object_name, response.context)


class TestCategoryDetailView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='movies')
        blogposts = BlogPostFactory.create_batch(10, is_published=True)
        cls.category.blogposts.add(*blogposts)
        unpublished_blogpost = BlogPostFactory.create(is_published=False)
        cls.category.blogposts.add(unpublished_blogpost)
    
    def test_view_accessible_at_location(self):
        response = self.client.get(f'/blog/categories/{self.category.name}/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('blog:category-detail', kwargs={'name': self.category.name}))
        self.assertEqual(response.status_code, 200)
    
    def test_use_correct_template(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/category_detail.html')
    
    def test_use_correct_context_object_name(self):
        expected_context_object_name = 'category'
        response = self.client.get(self.category.get_absolute_url())
        self.assertIn(expected_context_object_name, response.context)
    
    def test_blogposts_are_in_context(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertIn('blogposts', response.context)

    def test_cannot_see_hidden_blogposts(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(len(response.context['blogposts']), 9)
        response = self.client.get(self.category.get_absolute_url() + '?page=2')
        self.assertEqual(len(response.context['blogposts']), 1)

    def test_blogposts_paginated_by_9(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertIn('paginator', response.context)
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['blogposts']), 9)