# Generated by Django 3.1.2 on 2022-04-19 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0007_auto_20220419_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_api',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='db_api',
            name='updata_time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
