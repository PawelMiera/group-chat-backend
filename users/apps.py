from django.apps import AppConfig


# class UsersConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'users'
#     def ready(self):
#         from django.contrib.auth.models import User
#
#         user_exists = User.objects.filter(email="server@server.com").exists()
#
#         if not user_exists:
#             User.objects.create(email="server@server.com", username="server", password="abc")