# Generated by Django 5.0.6 on 2024-05-15 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0004_emailverify_alter_notice_created_alter_user_cities_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailverify',
            name='sendTime',
            field=models.DateTimeField(),
        ),
    ]
