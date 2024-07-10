from django.db import models

# Create your models here.

class TipoLicencias(models.Model):
    id_tipo_licencia = models.AutoField(primary_key=True)
    tipo_licencia = models.CharField(max_length=50)
    observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_licencias'