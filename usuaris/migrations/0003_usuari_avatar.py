# Generated by Django 4.1.7 on 2023-04-04 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '0002_usuari_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuari',
            name='avatar',
            field=models.FileField(default='<img src="https://issuestorage.s3.us-west-2.amazonaws.com/media/avatar/default.png" height="50" width="50" />', upload_to='', verbose_name='Avatar'),
        ),
    ]
