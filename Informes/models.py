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

class Motivo(models.Model):
    id_motivo = models.AutoField(primary_key=True)
    nombre_motivo = models.CharField(max_length=20, null=False)
    descripcion_motivo = models.CharField(max_length=500, null=False)
    estado_motivo = models.IntegerField(null=False, choices=[(0, 'Inactive'), (1, 'Active')])

    class Meta:
        managed = False  # Indica que Django no maneja esta tabla (puede ser gestionada por otra aplicación)
        db_table = 'motivo'

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
    secuencia_solicitud = models.IntegerField(blank=True, null=True)
    fecha_solicitud = models.DateField()
    motivo_movilizacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_salida_solicitud = models.DateField(blank=True, null=True)
    hora_salida_solicitud = models.TimeField(blank=True, null=True)
    fecha_llegada_solicitud = models.DateField(blank=True, null=True)
    hora_llegada_solicitud = models.TimeField(blank=True, null=True)
    descripcion_actividades = models.TextField(blank=True, null=True)
    listado_empleado = models.TextField(blank=True, null=True)
    estado_solicitud = models.CharField(max_length=50, blank=True, null=True)
    id_empleado = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='id_empleado')

    class Meta:
        managed = False
        db_table = 'solicitudes'

    def generar_codigo_solicitud(self):
        # Obtener empleado asociado a la solicitud
        empleado = self.id_empleado

        # Obtener datos de la persona asociada al empleado
        persona = empleado.id_persona
        primer_apellido = persona.apellidos.split()[0] if persona.apellidos else ''
        segundo_apellido = persona.apellidos.split()[1][0] if len(persona.apellidos.split()) > 1 else ''
        primer_nombre = persona.nombres.split()[0] if persona.nombres else ''
        segundo_nombre = persona.nombres.split()[1][0] if len(persona.nombres.split()) > 1 else ''

        # Obtener siglas de la unidad y estación asociadas al empleado
        unidad = Unidades.objects.get(id_unidad=empleado.id_cargo.id_unidad_id)
        siglas_unidad = unidad.siglas_unidad if unidad.siglas_unidad else ''
        estacion = unidad.id_estacion
        siglas_estacion = estacion.siglas_estacion if estacion.siglas_estacion else ''

        # Obtener año de la solicitud
        year_solicitud = self.fecha_solicitud.year

        # Construir el código de solicitud
        codigo_solicitud = f'{self.secuencia_solicitud:03}-{primer_apellido[0]}{segundo_apellido[0]}{primer_nombre[0]}{segundo_nombre[0]}-{siglas_unidad}-INIAP-{siglas_estacion}-{year_solicitud}'

        return codigo_solicitud


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


class CategoriasBienes(models.Model):
    id_categorias_bien = models.AutoField(primary_key=True)
    descripcion_categoria = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'categorias_bienes'

class SubcategoriasBienes(models.Model):
    id_subcategoria_bien = models.AutoField(primary_key=True)
    id_categorias_bien = models.ForeignKey(CategoriasBienes, models.DO_NOTHING, db_column='id_categorias_bien')
    descripcion = models.CharField(max_length=255)
    identificador = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subcategorias_bienes'

class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    id_subcategoria_bien = models.ForeignKey(SubcategoriasBienes, models.DO_NOTHING, db_column='id_subcategoria_bien')
    placa = models.CharField(max_length=20)
    codigo_inventario = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=50, blank=True, null=True)
    color_primario = models.CharField(max_length=50, blank=True, null=True)
    color_secundario = models.CharField(max_length=50, blank=True, null=True)
    anio_fabricacion = models.IntegerField(blank=True, null=True)
    numero_motor = models.CharField(max_length=50, blank=True, null=True)
    numero_chasis = models.CharField(max_length=50, blank=True, null=True)
    numero_matricula = models.CharField(max_length=50, blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vehiculo'

class Bancos(models.Model):
    id_banco = models.AutoField(primary_key=True)
    nombre_banco = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'bancos'

class Provincias(models.Model):
    id_provincia = models.AutoField(primary_key=True)
    provincia = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'provincias'

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
    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)
    habilitado = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cuentas_bancarias'