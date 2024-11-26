from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models.functions import Now


class Command(BaseCommand):
    help = "Removes all inactive anonymous users"

    def handle(self, *args, **options):
        deleted = User.objects.filter(extendeduser__anonymous=True, last_login__lte=Now()-timedelta(days=1)).delete()
        print(deleted)
