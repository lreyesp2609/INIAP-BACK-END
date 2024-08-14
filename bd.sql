CREATE TABLE Provincias (
    id_provincia SERIAL PRIMARY KEY,
    Provincia VARCHAR(100) NOT NULL
);

CREATE TABLE Ciudades (
    id_ciudad SERIAL PRIMARY KEY,
    id_provincia INT NOT NULL,
    Ciudad VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_provincia) REFERENCES Provincias(id_provincia)
);

CREATE TABLE Rol (
    id_rol SERIAL PRIMARY KEY,
    rol VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255)
);

CREATE TABLE Motivo (
    id_motivo SERIAL PRIMARY KEY,
    nombre_motivo VARCHAR(20) NOT NULL,
    descripcion_motivo VARCHAR(500) NOT NULL,
    estado_motivo INTEGER NOT NULL CHECK (estado_motivo IN (0, 1))
);

CREATE TABLE Personas (
    id_persona SERIAL PRIMARY KEY,
    numero_cedula VARCHAR(20) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    genero VARCHAR(20),
    celular VARCHAR(20),
    direccion VARCHAR(255),
    correo_electronico VARCHAR(100)
);

CREATE TABLE Usuarios (
    id_usuario SERIAL PRIMARY KEY,
    id_rol INT NOT NULL,
    id_persona INT NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol),
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona)
);

CREATE TABLE Estaciones (
    id_estacion SERIAL PRIMARY KEY,
    nombre_estacion VARCHAR(100) NOT NULL,
    siglas_estacion VARCHAR(20),
    ruc VARCHAR(20),
    direccion VARCHAR(255),
    telefono VARCHAR(20)
);

CREATE TABLE Unidades (
    id_unidad SERIAL PRIMARY KEY,
    nombre_unidad VARCHAR(100) NOT NULL,
    siglas_unidad VARCHAR(20),
    id_estacion INT NOT NULL,
    FOREIGN KEY (id_estacion) REFERENCES Estaciones(id_estacion)
);


CREATE TABLE Cargos (
    id_cargo SERIAL PRIMARY KEY,
    id_unidad INT NOT NULL,
    cargo VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_unidad) REFERENCES Unidades(id_unidad)
);


CREATE TABLE Empleados (
    id_empleado SERIAL PRIMARY KEY,
    id_persona INT NOT NULL,
    id_cargo INT,
    distintivo VARCHAR(100),
    fecha_ingreso DATE,
    habilitado SMALLINT DEFAULT 1,
    FOREIGN KEY (id_persona) REFERENCES Personas(id_persona),
    FOREIGN KEY (id_cargo) REFERENCES Cargos(id_cargo)
);

CREATE TABLE Tipo_Licencias (
    id_tipo_licencia SERIAL PRIMARY KEY,
    tipo_licencia VARCHAR(50) NOT NULL,
    observacion VARCHAR(255)
);

CREATE TABLE Bancos (
    id_banco SERIAL PRIMARY KEY,
    nombre_banco VARCHAR(100) NOT NULL
);



CREATE TABLE Empleados_Tipo_Licencias (
    id_empleado INT NOT NULL,
    id_tipo_licencia INT NOT NULL,
    PRIMARY KEY (id_empleado, id_tipo_licencia),
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
    FOREIGN KEY (id_tipo_licencia) REFERENCES Tipo_Licencias(id_tipo_licencia)
);

CREATE TABLE Solicitudes (
    id_solicitud SERIAL PRIMARY KEY,
    secuencia_solicitud INT,
    fecha_solicitud DATE NOT NULL,
    motivo_movilizacion VARCHAR(255),
    lugar_servicio VARCHAR(255),
    fecha_salida_solicitud DATE,
    hora_salida_solicitud TIME,
    fecha_llegada_solicitud DATE,
    hora_llegada_solicitud TIME,
    descripcion_actividades TEXT,
    listado_empleado TEXT,
    estado_solicitud VARCHAR(50),
    id_empleado INT NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
);

CREATE TABLE Cuentas_Bancarias (
    id_cuenta_bancaria SERIAL PRIMARY KEY,
    id_banco INT NOT NULL,
    id_empleado INT NOT NULL,
    id_solicitud INT NOT NULL,
    tipo_cuenta VARCHAR(50),
    numero_cuenta VARCHAR(50),
    habilitado SMALLINT DEFAULT 1,
    FOREIGN KEY (id_banco) REFERENCES Bancos(id_banco),
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
    FOREIGN KEY (id_solicitud) REFERENCES Solicitudes(id_solicitud)
);


CREATE TABLE Transporte_Solicitudes (
    id_transporte_soli SERIAL PRIMARY KEY,
    id_solicitud INT NOT NULL,
    tipo_transporte_soli VARCHAR(50),
    nombre_transporte_soli VARCHAR(50),
    ruta_soli VARCHAR(255),
    fecha_salida_soli DATE,
    hora_salida_soli TIME,
    fecha_llegada_soli DATE,
    hora_llegada_soli TIME,
    FOREIGN KEY (id_solicitud) REFERENCES Solicitudes(id_solicitud)
);

CREATE TABLE Informes (
    id_informes SERIAL PRIMARY KEY,
    id_solicitud INT NOT NULL,
    fecha_informe DATE,
    fecha_salida_informe DATE,
    hora_salida_informe TIME,
    fecha_llegada_informe DATE,
    hora_llegada_informe TIME,
    evento VARCHAR(255),
    observacion TEXT,
    FOREIGN KEY (id_solicitud) REFERENCES Solicitudes(id_solicitud)
);

CREATE TABLE Actividades_Informes (
    id_informe INT NOT NULL,
    dia DATE,
    actividad VARCHAR(255),
    PRIMARY KEY (id_informe),
    FOREIGN KEY (id_informe) REFERENCES Informes(id_informes)
);

CREATE TABLE Facturas_Informes (
    id_informe INT NOT NULL,
    tipo_documento VARCHAR(50),
    fecha_emision DATE,
    detalle_documento VARCHAR(255),
    valor DECIMAL(10, 2),
    PRIMARY KEY (id_informe, tipo_documento),
    FOREIGN KEY (id_informe) REFERENCES Informes(id_informes)
);

CREATE TABLE Productos_Alcanzados_Informes (
    id_producto_alcanzado SERIAL PRIMARY KEY,
    id_informe INT NOT NULL,
    descripcion TEXT,
    FOREIGN KEY (id_informe) REFERENCES Informes(id_informes)
);

CREATE TABLE Transporte_Informe (
    id_transporte_informe SERIAL PRIMARY KEY,
    id_informe INT NOT NULL,
    tipo_transporte_info VARCHAR(50),
    nombre_transporte_info VARCHAR(100),
    ruta_info VARCHAR(255),
    fecha_salida_info DATE,
    hora_salida_info TIME,
    fecha_llegada_info DATE,
    hora_llegada_info TIME,
    FOREIGN KEY (id_informe) REFERENCES Informes(id_informes)
);

CREATE TABLE Categorias_Bienes (
    id_categorias_bien SERIAL PRIMARY KEY,
    descripcion_categoria VARCHAR(255) NOT NULL
);

CREATE TABLE Subcategorias_Bienes (
    id_subcategoria_bien SERIAL PRIMARY KEY,
    id_categorias_bien INT NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    identificador VARCHAR(50),
    FOREIGN KEY (id_categorias_bien) REFERENCES Categorias_Bienes(id_categorias_bien)
);

CREATE TABLE Vehiculo (
    id_vehiculo SERIAL PRIMARY KEY,
    id_subcategoria_bien INT NOT NULL,
    placa VARCHAR(20) NOT NULL,
    codigo_inventario VARCHAR(50),
    modelo VARCHAR(50),
    marca VARCHAR(100),
    color_primario VARCHAR(50),
    color_secundario VARCHAR(50),
    anio_fabricacion INTEGER,
    numero_motor VARCHAR(100),
    numero_chasis VARCHAR(100),
    numero_matricula VARCHAR(50),
    habilitado SMALLINT DEFAULT 1,
    FOREIGN KEY (id_subcategoria_bien) REFERENCES Subcategorias_Bienes(id_subcategoria_bien)
);


CREATE TABLE ordenes_movilizacion (
    id_orden_movilizacion SERIAL PRIMARY KEY,
    secuencial_orden_movilizacion VARCHAR(50) NOT NULL DEFAULT '000',
    fecha_hora_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo_movilizacion VARCHAR(50) NOT NULL,
    lugar_origen_destino_movilizacion VARCHAR(50) NOT NULL DEFAULT 'Mocache-Quevedo',
    duracion_movilizacion TIME NOT NULL,
    id_conductor INT NOT NULL,
    id_vehiculo INT NOT NULL,
    fecha_viaje DATE NOT NULL,
    hora_ida TIME NOT NULL,
    hora_regreso TIME NOT NULL,
    estado_movilizacion VARCHAR(50) NOT NULL DEFAULT 'En Espera',
    id_empleado INT NOT NULL,
    habilitado SMALLINT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_conductor) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculo(id_vehiculo),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

CREATE TABLE motivo_orden_movilizacion (
    id_motivo_orden SERIAL PRIMARY KEY,
    id_empleado INT NOT NULL,
    id_orden_movilizacion INT NOT NULL,
    motivo VARCHAR(250) NOT NULL, 
    fecha TIMESTAMP NOT NULL,

    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_orden_movilizacion) REFERENCES ordenes_movilizacion(id_orden_movilizacion)
);

CREATE TABLE horario_orden_movilizacion (
	id_horario_movilizacion SERIAL PRIMARY KEY,
    hora_ida_minima TIME NOT NULL,
    hora_llegada_maxima TIME NOT NULL,
    duracion_minima INT NOT NULL,
    duracion_maxima INT NOT NULL
);

CREATE TABLE rutas_movilizacion (
    id_ruta_movilizacion SERIAL PRIMARY KEY,
    ruta_origen VARCHAR(250) NOT NULL,
    ruta_destino VARCHAR(250) NOT NULL,
    ruta_descripcion VARCHAR(250) NOT NULL,
    ruta_estado VARCHAR(250) NOT NULL
); 