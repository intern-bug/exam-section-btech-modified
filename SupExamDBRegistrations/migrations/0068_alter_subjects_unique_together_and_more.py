# Generated by Django 4.0.4 on 2022-06-30 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SupExamDBRegistrations', '0067_alter_facultyassignment_co_ordinator_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subjects',
            unique_together={('SubCode', 'RegEventId')},
        ),
        migrations.AlterUniqueTogether(
            name='subjects_staging',
            unique_together={('SubCode', 'RegEventId')},
        ),
    ]
