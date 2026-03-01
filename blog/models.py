from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField


class BlogPost(models.Model):
    title = models.CharField(verbose_name=_('title'), max_length=100)
    content = HTMLField(verbose_name=_('content'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='blog_posts', null=True)
    last_edited_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(verbose_name=_('is published'), default=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Like')
    categories = models.ManyToManyField('Category', related_name='blogposts')
    view_count = models.PositiveBigIntegerField(default=0, blank=True, null=True)

    @property
    def get_author_username_display(self):
        return self.author.username if self.author and self.author.is_active else 'Anonymous'

    def get_absolute_url(self):
        return reverse("blog:blog-detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f'{self.title} ({self.author.username})'
    
    class Meta:
        ordering = ('-last_edited_date',)
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')


class Comment(models.Model):
    text = models.TextField(verbose_name=_('text'), max_length=300)
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='comments', null=True)
    last_edited_date = models.DateTimeField(auto_now=True)

    @property
    def get_author_username_display(self):
        return self.author.username if self.author and self.author.is_active else 'Anonymous'

    def __str__(self):
        return f'{self.text[:30]}… ({self.author.username})'
    
    class Meta:
        ordering = ('last_edited_date',)
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')


class Like(models.Model):
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('blog_post', 'user')
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')


class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, unique=True, verbose_name=_('name'))

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("blog:category-detail", kwargs={"name": self.name})

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')