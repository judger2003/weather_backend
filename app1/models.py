from django.db import models


# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=18, null=False, unique=True)
    password = models.CharField(max_length=100, null=False)
    avatar = models.CharField(max_length=200, default='static/default.png')
    phone = models.CharField(max_length=15, null=True)
    email = models.CharField(max_length=40, null=True)
    isAdmin = models.BooleanField(default=False)
    cities = models.CharField(max_length=500, null=True, default='')


class Feedback(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    reply = models.CharField(max_length=1000, null=True)
    status = models.CharField(max_length=40, default='未处理')
    updated = models.DateTimeField(auto_now=True)
    # 外键
    userId = models.ForeignKey(User, on_delete=models.CASCADE)


class Warning(models.Model):
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    type = models.CharField(max_length=20)
    content = models.CharField(max_length=300)
    warningTime = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)


class Notice(models.Model):
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    tag = models.CharField(max_length=40)
