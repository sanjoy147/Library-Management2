# Generated by Django 5.0.3 on 2024-03-25 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_remove_borrow_status_borrowrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrowrequest',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected')], default='P', max_length=1),
        ),
    ]
