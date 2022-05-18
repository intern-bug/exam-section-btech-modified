# Generated by Django 3.2.5 on 2022-04-13 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupExamDB', '0008_auto_20220408_1925'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AYear', models.IntegerField()),
                ('ASem', models.IntegerField()),
                ('BYear', models.IntegerField()),
                ('BSem', models.IntegerField()),
                ('Dept', models.IntegerField()),
                ('Status', models.IntegerField()),
            ],
            options={
                'db_table': 'RegistrationStatus',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StudentRegistrations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RegNo', models.IntegerField()),
                ('SubCode', models.CharField(max_length=10)),
                ('AYear', models.IntegerField()),
                ('ASem', models.IntegerField()),
                ('OfferedYear', models.IntegerField()),
                ('Dept', models.IntegerField()),
                ('BYear', models.IntegerField()),
                ('Regulation', models.IntegerField()),
                ('BSem', models.IntegerField()),
                ('Mode', models.IntegerField()),
            ],
            options={
                'db_table': 'StudentRegistrations',
                'managed': False,
            },
        ),
    ]
