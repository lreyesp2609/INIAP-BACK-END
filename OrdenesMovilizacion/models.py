from django.db import models

class OrdenesMovilizacion(models.Model):
    id_orden_movilizacion = models.AutoField(primary_key=True)
    secuencial_orden_movilizacion = models.CharField(max_length=50)
    fecha_hora_emision = models.DateTimeField()
    fecha_desde = models.DateField()
    hora_desde = models.TimeField()
    fecha_hasta = models.DateField()
    hora_hasta = models.TimeField()
    habilitado = models.BooleanField(default=True)

    class Meta:
        managed = False  
        db_table = 'ordenes_movilizacion'  
