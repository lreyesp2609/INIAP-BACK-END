from django.db import models

from Provincias.models import Provincias

# Create your models here.
class Ciudades(models.Model):
    id_ciudad = models.AutoField(primary_key=True)
    id_provincia = models.ForeignKey(Provincias, models.DO_NOTHING, db_column='id_provincia')
    ciudad = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ciudades'