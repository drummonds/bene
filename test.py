from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

User.objects.filter(email='admin@example.com').delete()
User.objects.create_superuser('admin@example.com', 'admin', 'nimda')

#from django.contrib.auth.models import User
#>>> user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
from django.contrib.auth import get_user_model
User = get_user_model()

