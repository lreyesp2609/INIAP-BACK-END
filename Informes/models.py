from django.db import models

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


class Solicitudes(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    fecha_solicitud = models.DateField()
    motivo_movilizacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_salida_solicitud = models.DateField(blank=True, null=True)
    hora_salida_solicitud = models.TimeField(blank=True, null=True)
    fecha_llegada_solicitud = models.DateField(blank=True, null=True)
    hora_llegada_solicitud = models.TimeField(blank=True, null=True)
    descripcion_actividades = models.TextField(blank=True, null=True)
    listado_empleado = models.TextField(blank=True, null=True)
    estado_solicitud = models.CharField(max_length=50, blank=True, null=True)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')

    class Meta:
        managed = False
        db_table = 'solicitudes'


class Informes(models.Model):
    id_informes = models.AutoField(primary_key=True)
    id_solicitud = models.ForeignKey('Solicitudes', models.DO_NOTHING, db_column='id_solicitud')
    secuencia_informe = models.IntegerField(blank=True, null=True)
    fecha_informe = models.DateField(blank=True, null=True)
    fecha_salida_informe = models.DateField(blank=True, null=True)
    hora_salida_informe = models.TimeField(blank=True, null=True)
    fecha_llegada_informe = models.DateField(blank=True, null=True)
    hora_llegada_informe = models.TimeField(blank=True, null=True)
    evento = models.CharField(max_length=255, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'informes'


class FacturasInformes(models.Model):
    id_informe = models.OneToOneField('Informes', models.DO_NOTHING, db_column='id_informe', primary_key=True)  # The composite primary key (id_informe, tipo_documento) found, that is not supported. The first column is selected.
    tipo_documento = models.CharField(max_length=50)
    fecha_emision = models.DateField(blank=True, null=True)
    detalle_documento = models.CharField(max_length=255, blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'facturas_informes'
        unique_together = (('id_informe', 'tipo_documento'),)


class TransporteInforme(models.Model):
    id_transporte_informe = models.AutoField(primary_key=True)
    id_informe = models.ForeignKey(Informes, models.DO_NOTHING, db_column='id_informe')
    tipo_transporte_info = models.CharField(max_length=50, blank=True, null=True)
    nombre_transporte_info = models.CharField(max_length=100, blank=True, null=True)
    ruta_info = models.CharField(max_length=255, blank=True, null=True)
    fecha_salida_info = models.DateField(blank=True, null=True)
    hora_salida_info = models.TimeField(blank=True, null=True)
    fecha_llegada_info = models.DateField(blank=True, null=True)
    hora_llegada_info = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transporte_informe'


class TransporteSolicitudes(models.Model):
    id_transporte_soli = models.AutoField(primary_key=True)
    id_solicitud = models.ForeignKey(Solicitudes, models.DO_NOTHING, db_column='id_solicitud')
    tipo_transporte_soli = models.CharField(max_length=50, blank=True, null=True)
    ruta_soli = models.CharField(max_length=255, blank=True, null=True)
    fecha_salida_soli = models.DateField(blank=True, null=True)
    hora_salida_soli = models.TimeField(blank=True, null=True)
    fecha_llegada_soli = models.DateField(blank=True, null=True)
    hora_llegada_soli = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transporte_solicitudes'


class ActividadesInformes(models.Model):
    id_informe = models.OneToOneField('Informes', models.DO_NOTHING, db_column='id_informe', primary_key=True)
    dia = models.DateField(blank=True, null=True)
    actividad = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actividades_informes'


class ProductosAlcanzadosInformes(models.Model):
    id_producto_alcanzado = models.AutoField(primary_key=True)
    id_informe = models.ForeignKey(Informes, models.DO_NOTHING, db_column='id_informe')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'productos_alcanzados_informes'