from django.db import models

class Encabezados(models.Model):
    id_encabezado = models.AutoField(primary_key=True)
    encabezado_superior = models.TextField(null=True, blank=True)
    encabezado_inferior = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'encabezados'
