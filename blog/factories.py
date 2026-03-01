from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.utils import timezone

import factory
from datetime import timedelta

from .models import BlogPost, Category

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    
    username = factory.Sequence(lambda n: f'User{n}')
    password = factory.LazyFunction(lambda: make_password('password'))
    is_staff = False

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add groups if passed during creation"""
        if not create:
            return
        
        if extracted:
            # extracted = list of Group instances
            for group in extracted:
                self.groups.add(group)


class BlogPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlogPost
    
    title = factory.Sequence(lambda n: f'Title {n}')
    content = factory.Faker('text')
    is_published = factory.Faker('pybool')
    author = factory.SubFactory(UserFactory)
