# Generated by Django 3.1.2 on 2022-04-28 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Myapp', '0009_auto_20220419_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='DB_project_host_folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=10, null=True)),
                ('name', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]
