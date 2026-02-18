from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group, Permission
from io import StringIO


class InitGroupsTest(TestCase):
    def test_creates_bloggers_group(self):
        out = StringIO()

        call_command('init_groups', stdout=out, stderr=StringIO())
        self.assertEqual(Group.objects.filter(name='bloggers').count(), 1)

        blogger_group = Group.objects.get(name='bloggers')
        blog_perms = set(
            [
                'add_blogpost',
                'change_blogpost',
                'delete_blogpost',
                'view_blogpost',
            ]
        )
        for perm in blogger_group.permissions.all():
            self.assertIn(perm.codename, blog_perms)
            blog_perms.discard(perm.codename)