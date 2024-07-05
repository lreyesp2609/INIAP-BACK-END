from django.db import models

from Unidades.models import Unidades

# Create your models here.
class Cargos(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    id_unidad = models.ForeignKey(Unidades, models.DO_NOTHING, db_column='id_unidad')
    cargo = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'cargos'
