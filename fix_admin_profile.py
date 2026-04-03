import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tms.settings')
django.setup()

from django.contrib.auth.models import User
from traffic.models import UserProfile

admin = User.objects.get(username='admin')
try:
    profile = admin.profile
    print("✓ Admin profile already exists")
except UserProfile.DoesNotExist:
    UserProfile.objects.create(user=admin, role='admin', department='ICT Unit', phone='+2348012345678')
    print("✓ Created missing admin profile")
