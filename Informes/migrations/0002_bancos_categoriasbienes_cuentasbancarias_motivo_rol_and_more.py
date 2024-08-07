# Generated by Django 5.0.6 on 2024-07-11 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Informes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bancos',
            fields=[
                ('id_banco', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_banco', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'bancos',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CategoriasBienes',
            fields=[
                ('id_categorias_bien', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion_categoria', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'categorias_bienes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CuentasBancarias',
            fields=[
                ('id_cuenta_bancaria', models.AutoField(primary_key=True, serialize=False)),
                ('tipo_cuenta', models.CharField(blank=True, max_length=50, null=True)),
                ('numero_cuenta', models.CharField(blank=True, max_length=50, null=True)),
                ('habilitado', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cuentas_bancarias',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Motivo',
            fields=[
                ('id_motivo', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_motivo', models.CharField(max_length=20)),
                ('descripcion_motivo', models.CharField(max_length=500)),
                ('estado_motivo', models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'db_table': 'motivo',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id_rol', models.AutoField(primary_key=True, serialize=False)),
                ('rol', models.CharField(max_length=50)),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'rol',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SubcategoriasBienes',
            fields=[
                ('id_subcategoria_bien', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=255)),
                ('identificador', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'subcategorias_bienes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('id_usuario', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.CharField(max_length=50)),
                ('contrasenia', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'usuarios',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Vehiculo',
            fields=[
                ('id_vehiculo', models.AutoField(primary_key=True, serialize=False)),
                ('placa', models.CharField(max_length=20)),
                ('codigo_inventario', models.CharField(blank=True, max_length=50, null=True)),
                ('modelo', models.CharField(blank=True, max_length=50, null=True)),
                ('marca', models.CharField(blank=True, max_length=50, null=True)),
                ('color_primario', models.CharField(blank=True, max_length=50, null=True)),
                ('color_secundario', models.CharField(blank=True, max_length=50, null=True)),
                ('anio_fabricacion', models.IntegerField(blank=True, null=True)),
                ('numero_motor', models.CharField(blank=True, max_length=50, null=True)),
                ('numero_chasis', models.CharField(blank=True, max_length=50, null=True)),
                ('numero_matricula', models.CharField(blank=True, max_length=50, null=True)),
                ('habilitado', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'vehiculo',
                'managed': False,
            },
        ),
    ]
