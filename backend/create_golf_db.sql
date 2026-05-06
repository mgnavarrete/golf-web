-- Script de referencia (manual)
-- Recomendado: usar backend/setup_golf_mysql.sh para tomar credenciales desde .env

CREATE DATABASE IF NOT EXISTS golf_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'golf_user'@'localhost' IDENTIFIED BY 'CAMBIA_POR_TU_DB_PASSWORD';
ALTER USER 'golf_user'@'localhost' IDENTIFIED BY 'CAMBIA_POR_TU_DB_PASSWORD';

GRANT ALL PRIVILEGES ON golf_db.* TO 'golf_user'@'localhost';
FLUSH PRIVILEGES;
