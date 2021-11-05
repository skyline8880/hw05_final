# Generated by Django 2.2.19 on 2021-09-10 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210909_2033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group', to='posts.Group'),
        ),
    ]
