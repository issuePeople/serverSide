# Generated by Django 4.1.7 on 2023-04-02 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0006_issue_bloquejat_issue_motiubloqueig_alter_issue_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True, verbose_name='Data penjat')),
                ('document', models.FileField(upload_to='', verbose_name='Document')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issues.issue', verbose_name='Issue')),
            ],
        ),
    ]
