BEGIN;
-- Insertar estación
INSERT INTO Estaciones (nombre_estacion, siglas_estacion, ruc, direccion, telefono)
VALUES
  (
    'Estación Experimental Tropical Pichilingue',  -- Nombre de la estación
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
    (SELECT id_estacion FROM Estaciones WHERE nombre_estacion = 'Estación Experimental Tropical Pichilingue')  -- id_estacion
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
        (SELECT id_rol FROM Rol WHERE rol = 'Empleado'),  -- Reemplaza con el ID del rol 'Empleado'
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
