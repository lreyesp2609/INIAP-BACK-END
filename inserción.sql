BEGIN;
-- Insertar estación
INSERT INTO Estaciones (nombre_estacion, siglas_estacion, ruc, direccion, telefono)
VALUES
  (
    'ESTACIÓN EXPERIMENTAL TROPICAL PICHILINGUE',  -- Nombre de la estación
    'EETP',                                       -- Siglas de la estación
    '1',                                          -- RUC
    'Vía a El Empalme, Quevedo',                  -- Dirección
    '(05) 278-3044'                               -- Teléfono
  );

-- Insertar unidad
INSERT INTO Unidades (nombre_unidad, siglas_unidad, id_estacion)
VALUES
  (
    'UNIDAD DE INFORMATICA',  -- Nombre de la unidad
    'UI',                     -- Siglas de la unidad
    (SELECT id_estacion FROM Estaciones WHERE nombre_estacion = 'ESTACIÓN EXPERIMENTAL TROPICAL PICHILINGUE')  -- id_estacion
  );

-- Insertar cargo
INSERT INTO Cargos (id_unidad, cargo)
VALUES
  (
    (SELECT id_unidad FROM Unidades WHERE nombre_unidad = 'UNIDAD DE INFORMATICA'),  -- id_unidad
    'ASISTENTE TIC 1 DE ESTACION EXPERIMENTAL'                                      -- Cargo
  );

-- Inserta usuario para admin
INSERT INTO auth_user (
    password,
    last_login,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined
) VALUES (
    'pbkdf2_sha256$720000$nA1DBiCSy5A4HPTMAfMGDx$MmlhOsKKop+XKgi48HY1WYVShwtU6vD1/nsc8bnk2Zo=', -- Reemplaza con la contraseña cifrada
    NULL,              -- last_login, puedes dejarlo como NULL
    true,              -- is_superuser, puede ser true o false según tus necesidades
    'admin1',
    'luis',
    'reyes',
    'correo@example.com',
    true,              -- is_staff, puede ser true o false según tus necesidades
    true,              -- is_active, puede ser true o false según tus necesidades
    current_timestamp   -- date_joined, utiliza la fecha y hora actual
);

-- Insertar roles
INSERT INTO Rol (rol, descripcion)
VALUES
  ('Administrador', 'Rol con acceso completo al sistema'),
  ('Empleado', 'Rol para usuarios regulares'),
  ('SuperUsuario', 'Rol para supervisores de unidades');

-- Insertar persona
INSERT INTO Personas (numero_cedula, nombres, apellidos, fecha_nacimiento, genero, celular, direccion, correo_electronico)
VALUES
  (
    '0123456789',       -- Número de cédula
    'Luis',             -- Nombres
    'Reyes',            -- Apellidos
    '2002-09-26',       -- Fecha de nacimiento (ejemplo)
    'Masculino',        -- Género
    '0991234567',       -- Celular
    'Av. Principal 123',-- Dirección
    'luis@example.com'  -- Correo electrónico
  );


INSERT INTO Motivo (nombre_motivo, descripcion_motivo, estado_motivo) VALUES
('Viáticos', 'Gastos relacionados con viajes de trabajo.', 1),
('Movilizaciones', 'Gastos de transporte durante la jornada laboral.', 1),
('Subsistencias', 'Gastos diarios de mantenimiento personal.', 1),
('Alimentación', 'Gastos de comidas durante la jornada laboral.', 1);

INSERT INTO Provincias (Provincia) VALUES
('Azuay'),
('Bolívar'),
('Cañar'),
('Carchi'),
('Chimborazo'),
('Cotopaxi'),
('El Oro'),
('Esmeraldas'),
('Galápagos'),
('Guayas'),
('Imbabura'),
('Loja'),
('Los Ríos'),
('Manabí'),
('Morona Santiago'),
('Napo'),
('Orellana'),
('Pastaza'),
('Pichincha'),
('Santa Elena'),
('Santo Domingo de los Tsáchilas'),
('Sucumbíos'),
('Tungurahua'),
('Zamora Chinchipe');

INSERT INTO Ciudades (id_provincia, Ciudad) VALUES
-- Azuay
(1, 'Cuenca'),
(1, 'Gualaceo'),
(1, 'Sigsig'),
(1, 'Chordeleg'),
(1, 'El Pan'),
(1, 'Nabón'),
(1, 'Paute'),
(1, 'Santa Isabel'),
-- Bolívar
(2, 'Guaranda'),
(2, 'Caluma'),
(2, 'Chillanes'),
(2, 'Chimbo'),
(2, 'San Miguel'),
-- Cañar
(3, 'Azogues'),
(3, 'Biblián'),
(3, 'Cañar'),
(3, 'La Troncal'),
(3, 'Déleg'),
-- Carchi
(4, 'Tulcán'),
(4, 'Bolívar'),
(4, 'Espejo'),
(4, 'Mira'),
(4, 'Montúfar'),
(4, 'San Gabriel'),
-- Chimborazo
(5, 'Riobamba'),
(5, 'Alausí'),
(5, 'Colta'),
(5, 'Cumandá'),
(5, 'Guamote'),
(5, 'Chambo'),
(5, 'Chunchi'),
(5, 'Colta'),
-- Cotopaxi
(6, 'Latacunga'),
(6, 'La Mana'),
(6, 'Pangua'),
(6, 'Pujilí'),
(6, 'Salcedo'),
(6, 'Sigchos'),
-- El Oro
(7, 'Machala'),
(7, 'Arenillas'),
(7, 'Atahualpa'),
(7, 'Balsas'),
(7, 'Chilla'),
(7, 'El Guabo'),
(7, 'Huaquillas'),
(7, 'Las Lajas'),
(7, 'Marcabelí'),
(7, 'Pasaje'),
(7, 'Piñas'),
(7, 'Portovelo'),
(7, 'Santa Rosa'),
-- Esmeraldas
(8, 'Esmeraldas'),
(8, 'Atacames'),
(8, 'Eloy Alfaro'),
(8, 'Muisne'),
(8, 'Quinindé'),
(8, 'Rioverde'),
(8, 'San Lorenzo'),
-- Galápagos
(9, 'San Cristóbal'),
(9, 'Isabela'),
(9, 'Santa Cruz'),
-- Guayas
(10, 'Guayaquil'),
(10, 'Alfredo Baquerizo Moreno (Jujan)'),
(10, 'Balao'),
(10, 'Balzar'),
(10, 'Colimes'),
(10, 'Daule'),
(10, 'Durán'),
(10, 'El Empalme'),
(10, 'El Triunfo'),
(10, 'Milagro'),
(10, 'Naranjal'),
(10, 'Naranjito'),
(10, 'Palestina'),
(10, 'Pedro Carbo'),
(10, 'Samborondón'),
(10, 'Santa Lucía'),
(10, 'Simón Bolívar'),
(10, 'Yaguachi'),
(10, 'General Antonio Elizalde (Bucay)'),
(10, 'Isidro Ayora'),
-- Imbabura
(11, 'Ibarra'),
(11, 'Antonio Ante'),
(11, 'Cotacachi'),
(11, 'Otavalo'),
(11, 'Pimampiro'),
(11, 'San Miguel de Urcuquí'),
-- Loja
(12, 'Loja'),
(12, 'Calvas'),
(12, 'Catamayo'),
(12, 'Celica'),
(12, 'Chaguarpamba'),
(12, 'Espíndola'),
(12, 'Gonzanamá'),
(12, 'Macará'),
(12, 'Paltas'),
(12, 'Puyango'),
(12, 'Saraguro'),
(12, 'Sozoranga'),
(12, 'Zapotillo'),
-- Los Ríos
(13, 'Babahoyo'),
(13, 'Baba'),
(13, 'Buena Fé'),
(13, 'Mocache'),
(13, 'Montalvo'),
(13, 'Palenque'),
(13, 'Pueblo Viejo'),
(13, 'Quevedo'),
(13, 'Urdaneta'),
(13, 'Valencia'),
(13, 'Ventanas'),
(13, 'Vinces'),
-- Manabí
(14, 'Portoviejo'),
(14, 'Bolívar'),
(14, 'Chone'),
(14, 'El Carmen'),
(14, 'Flavio Alfaro'),
(14, 'Jipijapa'),
(14, 'Junín'),
(14, 'Manta'),
(14, 'Montecristi'),
(14, 'Paján'),
(14, 'Pichincha'),
(14, 'Rocafuerte'),
(14, 'Santa Ana'),
(14, 'Sucre'),
(14, 'Tosagua'),
(14, '24 de Mayo'),
-- Morona Santiago
(15, 'Macas'),
(15, 'Sucúa'),
(15, 'Huamboya'),
(15, 'Logroño'),
(15, 'Morona'),
(15, 'Pablo Sexto'),
(15, 'Palora'),
(15, 'San Juan Bosco'),
(15, 'San José de Morona'),
-- Napo
(16, 'Tena'),
(16, 'Archidona'),
(16, 'Carlos Julio Arosemena Tola'),
(16, 'El Chaco'),
(16, 'Quijos'),
-- Orellana
(17, 'Francisco de Orellana (El Coca)'),
(17, 'Aguarico'),
(17, 'La Joya de los Sachas'),
(17, 'Loreto'),
-- Pastaza
(18, 'Puyo'),
(18, 'Arajuno'),
(18, 'Mera'),
(18, 'Santa Clara'),
(18, 'Shushufindi'),
-- Pichincha
(19, 'Quito'),
(19, 'Cayambe'),
(19, 'Mejía'),
(19, 'Pedro Moncayo'),
(19, 'Pedro Vicente Maldonado'),
(19, 'Puerto Quito'),
(19, 'Rumiñahui'),
-- Santa Elena
(20, 'Santa Elena'),
(20, 'La Libertad'),
(20, 'Salinas'),
-- Santo Domingo de los Tsáchilas
(21, 'Santo Domingo'),
(21, 'La Concordia'),
-- Sucumbíos
(22, 'Nueva Loja'),
(22, 'Cascales'),
(22, 'Cuyabeno'),
(22, 'Gonzalo Pizarro'),
(22, 'Putumayo'),
(22, 'Shushufindi'),
-- Tungurahua
(23, 'Ambato'),
(23, 'Baños de Agua Santa'),
(23, 'Cevallos'),
(23, 'Mocha'),
(23, 'Patate'),
(23, 'Quero'),
(23, 'Quito'),
-- Zamora Chinchipe
(24, 'Zamora'),
(24, 'Centinela del Cóndor'),
(24, 'Chinchipe'),
(24, 'El Pangui'),
(24, 'Nangaritza'),
(24, 'Palanda'),
(24, 'Paquisha'),
(24, 'Yacuambi'),
(24, 'Yantzaza');


-- Obtener el id_persona recién insertado
DO $$
DECLARE
    persona_id INT;
    cargo_id INT;
BEGIN
    -- Obtener el id_persona recién insertado
    SELECT id_persona INTO persona_id FROM Personas WHERE numero_cedula = '0123456789';

    -- Obtener el id_cargo de 'ASISTENTE TIC 1 DE ESTACION EXPERIMENTAL'
    SELECT id_cargo INTO cargo_id FROM Cargos WHERE cargo = 'ASISTENTE TIC 1 DE ESTACION EXPERIMENTAL';

    -- Insertar usuario Empleado
    INSERT INTO Usuarios (id_rol, id_persona, usuario, contrasenia)
    VALUES
    (
        (SELECT id_rol FROM Rol WHERE rol = 'SuperUsuario'),  -- Reemplaza con el ID del rol 'Empleado'
        persona_id,  -- id_persona recién obtenido
        'luis.reyes',  -- Usuario
        'pbkdf2_sha256$720000$nA1DBiCSy5A4HPTMAfMGDx$MmlhOsKKop+XKgi48HY1WYVShwtU6vD1/nsc8bnk2Zo='  -- Contraseña cifrada
    );

    -- Insertar en Empleados
    INSERT INTO Empleados (id_persona, id_cargo, fecha_ingreso, habilitado)
    VALUES
    (
        persona_id,  -- id_persona recién obtenido
        cargo_id,    -- id_cargo recién obtenido
        current_date, -- Fecha de ingreso actual
        1            -- Habilitado (1 para true)
    );
END $$;

COMMIT;
