-- ============================================
-- 1. CREAR BASE DE DATOS
-- ============================================
DROP DATABASE IF EXISTS printsafe_ai;

CREATE DATABASE printsafe_ai
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE printsafe_ai;


-- ============================================
-- 2. TABLA: EMPLEADO
-- (empleado fijo id=1 para registrar análisis)
-- ============================================
DROP TABLE IF EXISTS empleado;

CREATE TABLE empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombres     VARCHAR(120) NOT NULL,
    apellidos   VARCHAR(120) NOT NULL,
    celular     VARCHAR(20),
    rol         VARCHAR(50) DEFAULT 'Operador'
);

-- INSERTAR EMPLEADO FIJO PARA TODO EL SISTEMA
INSERT INTO empleado (nombres, apellidos, celular, rol)
VALUES ('Sistema', 'PrintSafe', '999999999', 'Operador');


-- ============================================
-- 3. TABLA: CLIENTE
-- ============================================
DROP TABLE IF EXISTS cliente;

CREATE TABLE cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombres    VARCHAR(120) NOT NULL,
    apellidos  VARCHAR(120) NOT NULL,
    dni_ruc    VARCHAR(20),
    celular    VARCHAR(20),
    empresa    VARCHAR(150)
);


-- ============================================
-- 4. TABLA: IMAGEN ANALISIS
-- ============================================
DROP TABLE IF EXISTS imagen_analisis;

CREATE TABLE imagen_analisis (
    id_analisis    INT AUTO_INCREMENT PRIMARY KEY,

    id_empleado    INT NULL,
    id_cliente     INT NULL,

    nombre_archivo VARCHAR(255),
    resultado      VARCHAR(20),
    probabilidad   FLOAT,
    confianza      FLOAT,
    fecha          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    ruta_imagen    VARCHAR(300),
    comentarios    TEXT,

    CONSTRAINT fk_imagen_empleado
        FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT fk_imagen_cliente
        FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
        ON DELETE SET NULL ON UPDATE CASCADE
);
USE printsafe_ai;
SELECT * FROM cliente;
USE printsafe_ai;
SELECT * FROM imagen_analisis;
