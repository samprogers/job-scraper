# Generated by Django 4.2.23 on 2025-07-14 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datascraper', '0015_alter_jobposting_skills'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=50)),
                ('subcategory', models.CharField(max_length=50)),
                ('libraries', models.CharField(max_length=255)),
            ],
        ),
    ]
