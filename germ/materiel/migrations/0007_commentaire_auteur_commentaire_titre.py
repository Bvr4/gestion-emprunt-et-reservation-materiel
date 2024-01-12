# Generated by Django 4.2.7 on 2024-01-12 14:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('materiel', '0006_commentaire'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentaire',
            name='auteur',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentaire',
            name='titre',
            field=models.CharField(default='titre', max_length=80),
            preserve_default=False,
        ),
    ]
