from django.apps import AppConfig


class AdminTestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tests"
    label = "admin_tests"
    verbose_name = "Flowbite Admin Test Models"
