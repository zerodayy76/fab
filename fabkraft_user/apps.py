from django.apps import AppConfig


class FabkraftUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fabkraft_user'



class FabkraftUserConfig(AppConfig):
    name = 'fabkraft_user'

    def ready(self):
        import fabkraft_user.signals