# Generated by Django 3.1.2 on 2022-04-06 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0003_auto_20220406_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='db_project_folder',
            name='project_folder_id',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
