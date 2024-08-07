# Generated by Django 5.0.6 on 2024-07-14 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
    ]
