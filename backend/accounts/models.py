"""
Custom User Model for NEXEVENT.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):

    # ---- Inner enum: one level of indentation inside User ----
    class Role(models.IntegerChoices):
        STUDENT = 1, 'Student'
        ORGANIZER = 2, 'Organizer'
        ADMIN = 3, 'Admin'

    # ---- Model fields: SAME level as "class Role", NOT inside it ----
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
        error_messages={
            'unique': 'A user with this email already exists.',
        },
    )

    username = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text='Public display name.',
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    student_id = models.CharField(
        max_length=20,
        blank=True,
        default='',
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        default='',
    )
    year_of_study = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    role = models.PositiveSmallIntegerField(
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
    )

    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_organizer(self):
        return self.role >= self.Role.ORGANIZER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN