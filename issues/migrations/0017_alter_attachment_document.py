# Generated by Django 4.1.7 on 2023-04-05 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0016_alter_log_tipus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='document',
            field=models.FileField(upload_to='attachment/', verbose_name='Document'),
        ),
    ]