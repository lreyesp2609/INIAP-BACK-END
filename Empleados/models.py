from django.db import models

from Cargos.models import Cargos
from Licencias.models import TipoLicencias

# Create your models here.

class Empleados(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey('Personas', models.DO_NOTHING, db_column='id_persona')
    id_cargo = models.ForeignKey(Cargos, models.DO_NOTHING, db_column='id_cargo', blank=True, null=True)
    distintivo = models.CharField(max_length=100, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)
    es_jefe = models.BooleanField(blank=True, null=True)
    es_director = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleados'

class Personas(models.Model):
    id_persona = models.AutoField(primary_key=True)
    numero_cedula = models.CharField(max_length=20)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    correo_electronico = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personas'

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    rol = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')
    id_persona = models.ForeignKey(Personas, models.DO_NOTHING, db_column='id_persona')
    usuario = models.CharField(max_length=50)
    contrasenia = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'usuarios'

class MotivoEmpleados(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    motivo = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'motivo_empleados'

class EmpleadosTipoLicencias(models.Model):
    id_empleado = models.OneToOneField(Empleados, models.DO_NOTHING, db_column='id_empleado', primary_key=True)
    id_tipo_licencia = models.ForeignKey(TipoLicencias, db_column='id_tipo_licencia', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'empleados_tipo_licencias'
        unique_together = (('id_empleado', 'id_tipo_licencia'),)
