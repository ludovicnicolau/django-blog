from django.contrib import admin
from django.utils.html import escape
from django.template.defaultfilters import truncatechars

from .models import BlogPost, Comment

# Register your models here.
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author__username', 'last_edited_date')
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_comment_text', 'author__username', 'last_edited_date')

    def truncated_comment_text(self, obj):
        return truncatechars(escape(obj.text), 30)
    truncated_comment_text.short_description = 'text'


admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Comment, CommentAdmin)