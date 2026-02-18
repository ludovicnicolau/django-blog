from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Setup initial groups and permission'

    def handle(self, *args, **options):
        bloggers_group, created = Group.objects.get_or_create(name='bloggers')

        if created:
            self.stdout.write(self.style.SUCCESS('Created bloggers group'))
        else:
            self.stdout.write(self.style.WARNING('bloggers group already exists'))
            return

        blogpost_contenttype = ContentType.objects.get_for_model(BlogPost)
        permissions = Permission.objects.filter(content_type=blogpost_contenttype)

        blog_perms = [
            'add_blogpost',
            'change_blogpost',
            'delete_blogpost',
            'view_blogpost',
        ]

        for perm in blog_perms:
            permission = permissions.get(codename=perm)
            bloggers_group.permissions.add(permission)
            self.stdout.write(f'Added {perm} to blogger group')

        self.stdout.write(self.style.SUCCESS('Groups setup complete!'))
        