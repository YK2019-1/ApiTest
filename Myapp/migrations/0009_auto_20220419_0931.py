# Generated by Django 3.1.2 on 2022-04-19 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0008_auto_20220419_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='db_project_folder',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='db_project_folder',
            name='create_user',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='db_project_folder',
            name='updata_time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='db_project_folder',
            name='updata_user',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
