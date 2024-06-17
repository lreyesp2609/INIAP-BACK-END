from django.db import models

# Create your models here.
class Estaciones(models.Model):
    id_estacion = models.AutoField(primary_key=True)
    nombre_estacion = models.CharField(max_length=100)
    siglas_estacion = models.CharField(max_length=20, blank=True, null=True)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estaciones'

class Unidades(models.Model):
    id_unidad = models.AutoField(primary_key=True)
    nombre_unidad = models.CharField(max_length=100)
    siglas_unidad = models.CharField(max_length=20, blank=True, null=True)
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='id_estacion')

    class Meta:
        managed = False
        db_table = 'unidades'

class Cargos(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    id_unidad = models.ForeignKey('Unidades', models.DO_NOTHING, db_column='id_unidad')
    cargo = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'cargos'