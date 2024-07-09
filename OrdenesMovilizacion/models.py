from django.db import models
from Empleados.models import Empleados  

class OrdenesMovilizacion(models.Model):
    id_orden_movilizacion = models.AutoField(primary_key=True)
    secuencial_orden_movilizacion = models.CharField(max_length=50)
    fecha_hora_emision = models.DateTimeField()
    fecha_viaje = models.DateField()
    hora_ida = models.TimeField()
    hora_regreso = models.TimeField()
    estado_movilizacion = models.CharField(max_length=50, blank=True, null=True)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    habilitado = models.BigIntegerField(default=1)

    class Meta:
        managed = False  
        db_table = 'ordenes_movilizacion'  

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

class Empleados(models.Model):
    id_empleado = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey('Personas', models.DO_NOTHING, db_column='id_persona')
    id_cargo = models.ForeignKey(Cargos, models.DO_NOTHING, db_column='id_cargo', blank=True, null=True)
    distintivo = models.CharField(max_length=100, blank=True, null=True)
    fecha_ingreso = models.DateField(blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empleados'


