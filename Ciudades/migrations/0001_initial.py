# Generated by Django 5.0.6 on 2024-08-18 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ciudades',
            fields=[
                ('id_ciudad', models.AutoField(primary_key=True, serialize=False)),
                ('ciudad', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'ciudades',
                'managed': False,
            },
        ),
    ]
