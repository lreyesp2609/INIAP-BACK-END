# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ActividadesInformes(models.Model):
    id_informe = models.OneToOneField('Informes', models.DO_NOTHING, db_column='id_informe', primary_key=True)
    dia = models.DateField(blank=True, null=True)
    actividad = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actividades_informes'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Bancos(models.Model):
    id_banco = models.AutoField(primary_key=True)
    nombre_banco = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'bancos'


class Cargos(models.Model):
    id_cargo = models.AutoField(primary_key=True)
    id_unidad = models.ForeignKey('Unidades', models.DO_NOTHING, db_column='id_unidad')
    cargo = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'cargos'


class CategoriasBienes(models.Model):
    id_categorias_bien = models.AutoField(primary_key=True)
    descripcion_categoria = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'categorias_bienes'


class Ciudades(models.Model):
    id_ciudad = models.AutoField(primary_key=True)
    id_provincia = models.ForeignKey('Provincias', models.DO_NOTHING, db_column='id_provincia')
    ciudad = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ciudades'


class CuentasBancarias(models.Model):
    id_cuenta_bancaria = models.AutoField(primary_key=True)
    id_banco = models.ForeignKey(Bancos, models.DO_NOTHING, db_column='id_banco')
    id_empleado = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='id_empleado')
    id_solicitud = models.ForeignKey('Solicitudes', models.DO_NOTHING, db_column='id_solicitud')
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cuentas_bancarias'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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


class EmpleadosTipoLicencias(models.Model):
    id_empleado = models.OneToOneField(Empleados, models.DO_NOTHING, db_column='id_empleado', primary_key=True)  # The composite primary key (id_empleado, id_tipo_licencia) found, that is not supported. The first column is selected.
    id_tipo_licencia = models.ForeignKey('TipoLicencias', models.DO_NOTHING, db_column='id_tipo_licencia')

    class Meta:
        managed = False
        db_table = 'empleados_tipo_licencias'
        unique_together = (('id_empleado', 'id_tipo_licencia'),)

class Encabezados(models.Model):
    id_encabezado = models.AutoField(primary_key=True)
    encabezado_superior = models.TextField(null=True, blank=True)
    encabezado_inferior = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'encabezados'
        
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


class FacturasInformes(models.Model):
    id_factura = models.AutoField(primary_key=True)  # Clave primaria autoincremental
    id_informe = models.ForeignKey('Informes', on_delete=models.DO_NOTHING, db_column='id_informe')
    tipo_documento = models.CharField(max_length=50)
    numero_factura = models.CharField(max_length=50)
    fecha_emision = models.DateField(blank=True, null=True)
    detalle_documento = models.CharField(max_length=255, blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'facturas_informes'

class EstadoFactura(models.Model):
    id_estadofactura = models.AutoField(primary_key=True)  # Clave primaria autoincremental
    id_factura = models.ForeignKey(FacturasInformes, on_delete=models.CASCADE, db_column='id_factura')
    estado = models.IntegerField(choices=[(0, 'incompleto'), (1, 'completo')])

    class Meta:
        managed = False
        db_table = 'estado_factura'


class TotalFactura(models.Model):
    id_total = models.AutoField(primary_key=True)  # Clave primaria autoincremental
    id_factura = models.ForeignKey('FacturasInformes', on_delete=models.CASCADE, db_column='id_factura')
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'total_factura'


class HorarioOrdenMovilizacion(models.Model):
    id_horario_movilizacion = models.AutoField(primary_key=True)
    hora_ida_minima = models.TimeField()
    hora_llegada_maxima = models.TimeField()
    duracion_minima = models.IntegerField()
    duracion_maxima = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'horario_orden_movilizacion'


class Informes(models.Model):
    id_informes = models.AutoField(primary_key=True)
    id_solicitud = models.ForeignKey('Solicitudes', models.DO_NOTHING, db_column='id_solicitud')
    fecha_informe = models.DateField(blank=True, null=True)
    fecha_salida_informe = models.DateField(blank=True, null=True)
    hora_salida_informe = models.TimeField(blank=True, null=True)
    fecha_llegada_informe = models.DateField(blank=True, null=True)
    hora_llegada_informe = models.TimeField(blank=True, null=True)
    evento = models.CharField(max_length=255, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    estado = models.IntegerField(choices=[(0, 'incompleto'), (1, 'completo')])


    class Meta:
        managed = False
        db_table = 'informes'


class Motivo(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    nombre_motivo = models.CharField(max_length=20)
    descripcion_motivo = models.CharField(max_length=500)
    estado_motivo = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'motivo'


class MotivoEmpleados(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    motivo = models.CharField(max_length=255)
    fecha = models.DateTimeField()
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')

    class Meta:
        managed = False
        db_table = 'motivo_empleados'


class MotivoOrdenMovilizacion(models.Model):
    id_motivo_orden = models.AutoField(primary_key=True)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado')
    id_orden_movilizacion = models.ForeignKey('OrdenesMovilizacion', models.DO_NOTHING, db_column='id_orden_movilizacion')
    motivo = models.CharField(max_length=250)
    fecha = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'motivo_orden_movilizacion'


class MotivoVehiculo(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    motivo = models.CharField(max_length=255)
    fecha = models.DateTimeField()
    id_vehiculo = models.ForeignKey('Vehiculo', models.DO_NOTHING, db_column='id_vehiculo')

    class Meta:
        managed = False
        db_table = 'motivo_vehiculo'


class OrdenesMovilizacion(models.Model):
    id_orden_movilizacion = models.AutoField(primary_key=True)
    secuencial_orden_movilizacion = models.CharField(max_length=50)
    fecha_hora_emision = models.DateTimeField()
    motivo_movilizacion = models.CharField(max_length=50)
    lugar_origen_destino_movilizacion = models.CharField(max_length=50)
    duracion_movilizacion = models.TimeField()
    id_conductor = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_conductor')
    id_vehiculo = models.ForeignKey('Vehiculo', models.DO_NOTHING, db_column='id_vehiculo')
    fecha_viaje = models.DateField()
    hora_ida = models.TimeField()
    hora_regreso = models.TimeField()
    estado_movilizacion = models.CharField(max_length=50)
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='id_empleado', related_name='ordenesmovilizacion_id_empleado_set')
    habilitado = models.SmallIntegerField()

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


class ProductosAlcanzadosInformes(models.Model):
    id_producto_alcanzado = models.AutoField(primary_key=True)
    id_informe = models.ForeignKey(Informes, models.DO_NOTHING, db_column='id_informe')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'productos_alcanzados_informes'


class Provincias(models.Model):
    id_provincia = models.AutoField(primary_key=True)
    provincia = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'provincias'


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    rol = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'


class RutasMovilizacion(models.Model):
    id_ruta_movilizacion = models.AutoField(primary_key=True)
    ruta_origen = models.CharField(max_length=250)
    ruta_destino = models.CharField(max_length=250)
    ruta_descripcion = models.CharField(max_length=250)
    ruta_estado = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'rutas_movilizacion'


class Solicitudes(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    secuencia_solicitud = models.IntegerField(blank=True, null=True)
    fecha_solicitud = models.DateField()
    motivo_movilizacion = models.CharField(max_length=255, blank=True, null=True)
    lugar_servicio = models.CharField(max_length=255, blank=True, null=True)
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


class MotivoCancelado(models.Model):
    id_motivo_cancelado = models.AutoField(primary_key=True)
    id_solicitud = models.ForeignKey(Solicitudes, models.DO_NOTHING, db_column='id_solicitud')
    motivo_cancelado = models.TextField()

    class Meta:
        managed = False
        db_table = 'motivo_cancelado'


class SubcategoriasBienes(models.Model):
    id_subcategoria_bien = models.AutoField(primary_key=True)
    id_categorias_bien = models.ForeignKey(CategoriasBienes, models.DO_NOTHING, db_column='id_categorias_bien')
    descripcion = models.CharField(max_length=255)
    identificador = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcategorias_bienes'


class TipoLicencias(models.Model):
    id_tipo_licencia = models.AutoField(primary_key=True)
    tipo_licencia = models.CharField(max_length=50)
    observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_licencias'


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
    nombre_transporte_soli = models.CharField(max_length=50, blank=True, null=True)
    ruta_soli = models.CharField(max_length=255, blank=True, null=True)
    fecha_salida_soli = models.DateField(blank=True, null=True)
    hora_salida_soli = models.TimeField(blank=True, null=True)
    fecha_llegada_soli = models.DateField(blank=True, null=True)
    hora_llegada_soli = models.TimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transporte_solicitudes'


class Unidades(models.Model):
    id_unidad = models.AutoField(primary_key=True)
    nombre_unidad = models.CharField(max_length=100)
    siglas_unidad = models.CharField(max_length=20, blank=True, null=True)
    id_estacion = models.ForeignKey(Estaciones, models.DO_NOTHING, db_column='id_estacion')

    class Meta:
        managed = False
        db_table = 'unidades'


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')
    id_persona = models.ForeignKey(Personas, models.DO_NOTHING, db_column='id_persona')
    usuario = models.CharField(max_length=50)
    contrasenia = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'usuarios'


class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    id_subcategoria_bien = models.ForeignKey(SubcategoriasBienes, models.DO_NOTHING, db_column='id_subcategoria_bien')
    placa = models.CharField(max_length=20)
    codigo_inventario = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    color_primario = models.CharField(max_length=50, blank=True, null=True)
    color_secundario = models.CharField(max_length=50, blank=True, null=True)
    anio_fabricacion = models.IntegerField(blank=True, null=True)
    numero_motor = models.CharField(max_length=100, blank=True, null=True)
    numero_chasis = models.CharField(max_length=100, blank=True, null=True)
    numero_matricula = models.CharField(max_length=50, blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculo'
