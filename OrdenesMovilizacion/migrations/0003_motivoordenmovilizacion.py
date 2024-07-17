# Generated by Django 5.0.6 on 2024-07-17 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OrdenesMovilizacion', '0002_cargos_empleados_estaciones_personas_rol_unidades_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoOrdenMovilizacion',
            fields=[
                ('id_motivo_orden', models.AutoField(primary_key=True, serialize=False)),
                ('motivo', models.CharField(max_length=255)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'motivo_orden_movilizacion',
                'managed': False,
            },
        ),
    ]
