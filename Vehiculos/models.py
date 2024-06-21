from django.db import models

# Create your models here.
class CategoriasBienes(models.Model):
    id_categorias_bien = models.AutoField(primary_key=True)
    descripcion_categoria = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'categorias_bienes'

class SubcategoriasBienes(models.Model):
    id_subcategoria_bien = models.AutoField(primary_key=True)
    id_categorias_bien = models.ForeignKey(CategoriasBienes, models.DO_NOTHING, db_column='id_categorias_bien')
    descripcion = models.CharField(max_length=255)
    identificador = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcategorias_bienes'

class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    id_subcategoria_bien = models.ForeignKey(SubcategoriasBienes, models.DO_NOTHING, db_column='id_subcategoria_bien')
    placa = models.CharField(max_length=20)
    codigo_inventario = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    color_primario = models.CharField(max_length=50, blank=True, null=True)
    color_secundario = models.CharField(max_length=50, blank=True, null=True)
    anio_fabricacion = models.IntegerField(blank=True, null=True)
    numero_motor = models.CharField(max_length=50, blank=True, null=True)
    numero_chasis = models.CharField(max_length=50, blank=True, null=True)
    numero_matricula = models.CharField(max_length=50, blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculo'
