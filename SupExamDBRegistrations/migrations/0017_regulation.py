# Generated by Django 4.0.4 on 2022-05-24 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupExamDBRegistrations', '0016_studentregistrations_staging'),
    ]

    operations = [
        migrations.CreateModel(
            name='Regulation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AdmissionYear', models.IntegerField()),
                ('AYear', models.IntegerField()),
                ('BYear', models.IntegerField()),
                ('Regulation', models.IntegerField()),
            ],
            options={
                'db_table': 'Regulation',
            },
        ),
    ]
