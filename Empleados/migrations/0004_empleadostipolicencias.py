# Generated by Django 5.0.6 on 2024-07-11 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Empleados', '0003_motivoempleados'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmpleadosTipoLicencias',
            fields=[
                ('id_empleado', models.OneToOneField(db_column='id_empleado', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='Empleados.empleados')),
            ],
            options={
                'db_table': 'empleados_tipo_licencias',
                'managed': False,
            },
        ),
    ]