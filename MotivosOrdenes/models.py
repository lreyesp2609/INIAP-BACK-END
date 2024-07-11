from django.db import models

# Create your models here.
class Motivo(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    nombre_motivo = models.CharField(max_length=20, null=False)
    descripcion_motivo = models.CharField(max_length=500, null=False)
    estado_motivo = models.IntegerField(null=False, choices=[(0, 'Inactive'), (1, 'Active')])

    class Meta:
        managed = False
        db_table = 'motivo'