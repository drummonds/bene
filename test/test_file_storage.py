import os
from django.conf import settings

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


# What are the settings?
for x in ["AWS_ACCESS_KEY_ID", "AWS_STORAGE_BUCKET_NAME", "MEDIA_ROOT", "MEDIA_URL"]:
    try:
        value = getattr(settings, x)
        print(f'{x:20} = {value}')
    except AttributeError:
        print(f'{x:20} Doesn''t exist')

path = default_storage.save('squiggle', ContentFile(b'new content'))
print(path)
# path 'path/to/file'

with default_storage.open('squiggle2', 'w') as f:
    f.write('Hello djangonaut.\n')

print(default_storage.size(path))

print( default_storage.open(path).read())

# default_storage.delete(path)
print(f'Does the new file exist? {default_storage.exists(path)}')
