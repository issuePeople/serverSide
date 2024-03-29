# Generated by Django 4.1.7 on 2023-04-04 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '0006_alter_usuari_avatar'),
        ('issues', '0014_alter_log_issue_alter_log_usuari'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='issue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='logs', to='issues.issue', verbose_name='Issue'),
        ),
        migrations.AlterField(
            model_name='log',
            name='usuari',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='logs', to='usuaris.usuari', verbose_name='Usuari'),
        ),
    ]
