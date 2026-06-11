from django.core.files.storage import Storage
from django.conf import settings
from django.core.files.base import ContentFile
from supabase import create_client

import uuid


class SupabaseStorage(Storage):

    def __init__(self, bucket_name=None):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )
        self.bucket_name = bucket_name or 'media'

    def _save(self, name, content):
        last_slash_index = name.rfind('/')
        path = name[:last_slash_index+1]
        extension = name.split('.')[1]
        new_name = f'{path}{uuid.uuid()}.{extension}'

        self.client.storage.from_(self.bucket_name).upload(
            new_name,
            content.read(),
            {
                'content-type': content.content_type,
            }
        )

        return new_name
    
    def exists(self, name):
        return self.client.storage.from_(self.bucket_name).exists(name)
    
    def delete(self, name):
        self.client.storage.from_(self.bucket_name).remove([name])
    
    def url(self, name):
        return self.client.storage.from_(self.bucket_name).get_public_url(name)
    
    def _open(self, name, mode='rb'):
        response = self.client.storage.from_(self.bucket_name).download(name)

        return ContentFile(response, name=name)