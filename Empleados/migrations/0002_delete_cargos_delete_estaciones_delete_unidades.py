# Generated by Django 5.0.6 on 2024-07-09 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Empleados', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Cargos',
        ),
        migrations.DeleteModel(
            name='Estaciones',
        ),
        migrations.DeleteModel(
            name='Unidades',
        ),
    ]
