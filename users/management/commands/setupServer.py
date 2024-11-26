from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "SetupServer"

    def handle(self, *args, **options):
        from django.contrib.auth.models import User

        user_exists = User.objects.filter(email="server@server.com").exists()
        print("Server user exists", user_exists)

        if not user_exists:
            User.objects.create(email="server@server.com", username="server", password="abc")
            print("Created server user")