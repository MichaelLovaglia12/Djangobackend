from django.db import models
from django.utils import timezone
from .utils import send_emails

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class ConnectedEmail(models.Model):
    provider_name = models.CharField(max_length=255)
    email_address = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    smtp_host = models.CharField(max_length=255)
    smtp_port = models.CharField(max_length=200)
    smtp_username = models.CharField(max_length=255)
    smtp_password = models.CharField(max_length=255)
    imap_host = models.CharField(max_length=200)
    imap_port = models.CharField(max_length=200)
    imap_username = models.CharField(max_length=255)
    imap_password = models.CharField(max_length=255)

    def get_client_id(self):
        return self.client_id

    def get_secret_key(self):
        return self.secret_key

    def get_access_token(self):
        return self.access_token

    def get_refresh_token(self):
        return self.refresh_token

    def get_provider(self):
        return self.provider_name

    def set_access_token(self, token):
        self.access_token = token

    def set_refresh_token(self, token):
        self.refresh_token = token


class Lead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=100)
    website = models.URLField()

    def __str__(self):
        return self.name


class Campaign(models.Model):
    connected_email = models.ForeignKey(
        ConnectedEmail, on_delete=models.CASCADE)
    leads = models.ManyToManyField(Lead)
    message = models.TextField()
    scheduled_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.scheduled_time > timezone.now():
            send_emails.apply_async(
                (self.id,),
                eta=self.scheduled_time,
            )

    def __str__(self):
        return f"{self.connected_email.email} - {self.scheduled_time}"
