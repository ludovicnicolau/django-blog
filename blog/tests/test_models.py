from django.test import TestCase

from blog.models import BlogPost, Comment, Category
from django.contrib.auth import get_user_model

import time

User = get_user_model()


class BlogPostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create_user(username='Author', password='topsecret')
        BlogPost.objects.create(
            title='A simple title.',
            content='A very long text that should contains a lot of useful informations.',
            author=author,
            is_published=True
        )
        time.sleep(0.1)
        BlogPost.objects.create(
            title='A second post.',
            content='The content.',
            author=author,
            is_published=True
        )
        time.sleep(0.1)
        BlogPost.objects.create(
            title='A third post.',
            content='The content.',
            is_published=True
        )
    
    def test_title_label(self):
        post = BlogPost.objects.get(title='A simple title.')
        field_label = post._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_title_max_length(self):
        post = BlogPost.objects.get(title='A simple title.')
        title = post._meta.get_field('title')
        self.assertEqual(title.max_length, 100)
    
    def test_content_label(self):
        post = BlogPost.objects.get(title='A simple title.')
        content_label = post._meta.get_field('content').verbose_name
        self.assertEqual(content_label, 'content')
    
    def test_last_edited_date_label(self):
        post = BlogPost.objects.get(title='A simple title.')
        last_edited_date_label = post._meta.get_field('last_edited_date').verbose_name
        self.assertEqual(last_edited_date_label, 'last edited date')
    
    def test_is_published_label(self):
        post = BlogPost.objects.get(title='A simple title.')
        is_published_label = post._meta.get_field('is_published').verbose_name
        self.assertEqual(is_published_label, 'is published')
    
    def test_object_name_is_title_space_author_in_brackets(self):
        post = BlogPost.objects.get(title='A simple title.')
        expected_object_name = f'{post.title} ({post.author.username})'
        self.assertEqual(str(post), expected_object_name)
    
    def test_get_absolute_url(self):
        post = BlogPost.objects.get(title='A simple title.')
        self.assertEqual(post.get_absolute_url(), f'/blog/{post.slug}/')
    
    def test_ordered_most_recently_published_first(self):
        posts = BlogPost.objects.all()
        self.assertGreater(posts[0].published_date, posts[1].published_date)
    
    def test_get_author_username_display_with_existing_author(self):
        username = 'Author'
        post = BlogPost.objects.filter(author__username__exact=username)[0]
        self.assertEqual(username, post.get_author_username_display)
    
    def test_get_author_username_display_with_no_author(self):
        post = BlogPost.objects.get(title='A third post.')
        self.assertEqual('Anonymous', post.get_author_username_display)


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = User.objects.create_user(username='Author', password='topsecret')
        user = User.objects.create_user(username='Reader', password='topsecret')
        post = BlogPost.objects.create(title='The title', content='The content', author=author, is_published=True)
        Comment.objects.create(text='This is a comment about a blog post.', author=user, blog_post=post)
        time.sleep(0.1)
        Comment.objects.create(text='This is a second comment about a blog post.', author=user, blog_post=post)
        time.sleep(0.1)
        Comment.objects.create(text='This is a third comment about a blog post.', blog_post=post)
    
    def test_text_label(self):
        comment = Comment.objects.get(id=1)
        text_label = comment._meta.get_field('text').verbose_name
        self.assertEqual(text_label, 'text')
    
    def test_text_max_length(self):
        comment = Comment.objects.get(id=1)
        text_max_length = comment._meta.get_field('text').max_length
        self.assertEqual(text_max_length, 300)
    
    def test_object_name_is_30_letters_space_author_in_brackets(self):
        comment = Comment.objects.get(id=1)
        expected_str = f'{comment.text[:30]}… ({comment.author.username})'
        self.assertEqual(str(comment), expected_str)
    
    def test_ordered_oldest_to_most_recent(self):
        comments = Comment.objects.all()
        self.assertLess(comments[0].last_edited_date, comments[1].last_edited_date)
    
    def test_get_author_username_display_with_existing_author(self):
        username = 'Reader'
        comment = Comment.objects.filter(author__username__exact=username)[0]
        self.assertEqual(username, comment.get_author_username_display)
    
    def test_get_author_username_display_with_no_author(self):
        comment = Comment.objects.get(text='This is a third comment about a blog post.')
        self.assertEqual('Anonymous', comment.get_author_username_display)

class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='movies')
    
    def test_get_absolute_url(self):
        expected_url = f"/blog/categories/{self.category.name}/"
        self.assertEqual(expected_url, self.category.get_absolute_url())
    
    def test_name_label(self):
        label = self.category._meta.get_field('name').verbose_name
        expected_name = 'name'
        self.assertEqual(expected_name, label)
    
    def test_name_unique(self):
        is_unique = self.category._meta.get_field('name').unique
        self.assertTrue(is_unique)
    
    def test_name_not_null(self):
        is_null = self.category._meta.get_field('name').null
        self.assertFalse(is_null)
    
    def test_name_not_blank(self):
        is_blank = self.category._meta.get_field('name').blank
        self.assertFalse(is_blank)
    
    def test_object_name_is_name(self):
        self.assertEqual(str(self.category), self.category.name)
     