from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    published = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "admin_tests"
        ordering = ("title",)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.title
