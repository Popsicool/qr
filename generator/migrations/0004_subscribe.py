# Generated by Django 4.1.4 on 2022-12-14 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0003_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
            ],
        ),
    ]