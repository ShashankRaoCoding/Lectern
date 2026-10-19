from django.conf import settings
from django.db import models

from . import crypto


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    api_key_encrypted = models.TextField(blank=True)
    ai_model = models.CharField(max_length=100, blank=True, help_text="Blank = use the site default.")

    def set_api_key(self, key: str):
        self.api_key_encrypted = crypto.encrypt(key) if key else ""

    def get_api_key(self) -> str:
        return crypto.decrypt(self.api_key_encrypted) if self.api_key_encrypted else ""

    @property
    def masked_key(self) -> str:
        key = self.get_api_key()
        return f"…{key[-4:]}" if len(key) >= 8 else ("set" if key else "")

    def __str__(self):
        return f"Profile({self.user})"


class Textbook(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="textbooks")
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Section(models.Model):
    """One chunk of AI-written content, created from one uploaded .pptx."""

    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    source_filename = models.CharField(max_length=255, blank=True)
    markdown = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.textbook}: {self.title}"
