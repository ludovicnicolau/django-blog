from rest_framework import serializers

from .models import CustomUser

class BloggerSerializer(serializers.ModelSerializer):
    blogposts_count = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ('username', 'biography', 'date_joined', 'blogposts_count',)