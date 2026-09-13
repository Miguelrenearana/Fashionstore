-- Habilitar extensiones requeridas (docker-compose ejecuta este archivo al crear la BD;
-- en Neon debe ejecutarse manualmente una vez).
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";