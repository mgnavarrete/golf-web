#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No se encontró $ENV_FILE"
  exit 1
fi

get_env_var() {
  local key="$1"
  local value
  value=$(grep -E "^${key}=" "$ENV_FILE" | head -n 1 | cut -d '=' -f2-)
  echo "$value"
}

DB_NAME="$(get_env_var DB_NAME)"
DB_USER="$(get_env_var DB_USER)"
DB_PASSWORD="$(get_env_var DB_PASSWORD)"

if [[ -z "$DB_NAME" || -z "$DB_USER" || -z "$DB_PASSWORD" ]]; then
  echo "Faltan variables DB_NAME / DB_USER / DB_PASSWORD en backend/.env"
  exit 1
fi

# Escapar comillas simples para SQL
DB_PASSWORD_ESCAPED=${DB_PASSWORD//\'/\'\'}

echo "Creando base de datos '$DB_NAME' y usuario '$DB_USER' en MySQL..."

sudo mysql <<SQL
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD_ESCAPED';
ALTER USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD_ESCAPED';

GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "OK: base '$DB_NAME' y usuario '$DB_USER' listos."
