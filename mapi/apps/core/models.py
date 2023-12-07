from django.contrib.auth.models import (
    AbstractBaseUser,
)

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager

from uuid import uuid4


class UserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,date_joined=NOW(), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self,email,password=None,**extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser):

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    email = models.EmailField(
        _('email address'),
        max_length=255,
        unique=True,
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False
    )

    is_active = models.BooleanField(
        _('active status'),
        default=True
    )

    date_joined = models.DateTimeField(
        _('date joined'),
        auto_now_add=True
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

class Payment(models.Model):
    class Meta:
        db_table = 'payments'

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid4
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recipient = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('refunded', 'Refunded'),
            ('voided', 'Voided'),
        ],
        default='pending'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Additional fields
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Add other payment-related fields as needed

class Client(models.Model):
    class Meta:
        db_table = 'clients'

    client_id = models.CharField(max_length=255, unique=True)
    client_secret = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.client_id
