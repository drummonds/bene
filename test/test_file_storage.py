import datetime as dt
import json
from pathlib import Path

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

records = [["list"],[["another list"]]]
file_root = 'ContactGroup'
page = 0

filename = dt.datetime.now().strftime(f"XERO_DEBUG_%Y-%m-%dT%H-%M-%S_{file_root}_page_{page}.json")

print(f' Test filename for archiving {filename}')
with default_storage.open(filename, 'w') as f:
    json.dump(records,f)



print(default_storage.size(path))

print( default_storage.open(path).read())

# default_storage.delete(path)
print(f'Does the new file exist? {default_storage.exists(path)}')
