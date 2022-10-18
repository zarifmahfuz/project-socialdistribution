# Generated by Django 3.1.6 on 2022-10-18 01:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webserver', '0005_auto_20221017_0522'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inbox',
            old_name='author',
            new_name='target_author',
        ),
        migrations.RemoveField(
            model_name='inbox',
            name='accepted',
        ),
        migrations.RemoveField(
            model_name='inbox',
            name='requested',
        ),
        migrations.AddField(
            model_name='inbox',
            name='follow_request_acceptor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accepted_follow_requests', to='webserver.author', verbose_name='author who accepted the follow request'),
        ),
        migrations.AddField(
            model_name='inbox',
            name='follow_request_sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_follow_requests', to='webserver.author', verbose_name='author who sent the follow request'),
        ),
    ]
