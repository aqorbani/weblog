from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from datetime import datetime


def validate_file_extention(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    valid_extentions = ['.jpg', '.png']
    if not ext.lower() in valid_extentions:
        raise ValidationError('Unsupported file extension.')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.FileField(upload_to='files/user_avatar/', null=False, blank=False,
                              validators=[validate_file_extention])
    description = models.CharField(max_length=512, null=False, blank=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, null=False, blank=False)
    cover = models.FileField(upload_to='files/article_cover/', null=False, blank=False,
                             validators=[validate_file_extention])
    content = RichTextField()
    created_at = models.DateTimeField(default=datetime.now, blank=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    meta_description = models.CharField(default='', max_length=512, null=False, blank=False)
    meta_keywords = models.CharField(default='', max_length=512, null=False, blank=False)
    promote = models.BooleanField(default=False)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128, null=False, blank=False)
    cover = models.FileField(upload_to='files/category_cover/', null=False, blank=False,
                             validators=[validate_file_extention])
    # parent_id = models.ForeignKey('Category')

    def __str__(self):
        return self.title
