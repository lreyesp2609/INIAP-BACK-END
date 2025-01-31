from django.db import models

class Kilometraje(models.Model):
    id_kilometraje = models.AutoField(primary_key=True)
    id_vehiculo = models.ForeignKey(
        'Vehiculos.Vehiculo',
        on_delete=models.DO_NOTHING,
        db_column='id_vehiculo'
    )
    empleado = models.ForeignKey(  # Nuevo campo añadido
        'Empleados.Empleados',  # Asegúrate de que la app se llama correctamente
        on_delete=models.DO_NOTHING,
        db_column='id_empleado',
        verbose_name='Empleado registrador'
    )
    fecha_registro = models.DateField()
    kilometraje = models.IntegerField()
    evento = models.CharField(max_length=255)

    class Meta:
        managed = False  # Si es False, deberás aplicar manualmente los cambios en DB
        db_table = 'kilometraje'

class AlertasMantenimiento(models.Model):
    id_alerta = models.AutoField(primary_key=True)
    id_vehiculo = models.ForeignKey(
        'Vehiculos.Vehiculo',  # Relación con la tabla Vehiculo
        on_delete=models.DO_NOTHING,
        db_column='id_vehiculo'
    )
    kilometraje_activacion = models.IntegerField()
    tipo_mantenimiento = models.CharField(max_length=255)
    estado_alerta = models.BooleanField()

    class Meta:
        managed = False  # Cambiar a True si deseas que Django gestione la tabla
        db_table = 'alertas_mantenimiento'