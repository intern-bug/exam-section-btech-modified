# Generated by Django 4.0.4 on 2022-05-21 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SupExamDBRegistrations', '0014_delete_rolllists'),
    ]

    operations = [
        migrations.CreateModel(
            name='RollLists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RegNo', models.IntegerField()),
                ('Dept', models.IntegerField()),
                ('AYear', models.IntegerField()),
                ('BYear', models.IntegerField()),
                ('Cycle', models.IntegerField()),
            ],
            options={
                'db_table': 'RollLists',
                'managed': False,
            },
        ),
    ]
