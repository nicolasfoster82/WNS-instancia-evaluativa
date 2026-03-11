# WNS Challenge

Este `README.md` queda enfocado en la estructura del repositorio y en el setup tecnico base, en particular la base de datos PostgreSQL dockerizada.

## Estructura actual

- `consigna.md`: enunciado original del desafio.
- `inputs/`: archivos entregados por la consigna.
- `docs/der.png`: diagrama entidad relacion de la base.
- `docker-compose.yml`: servicio PostgreSQL con Docker.
- `docker/postgres/init/01_schema.sql`: esquema inicial de la base.

## DER

![DER de la base de datos](docs/der.png)

## Programas necesarios

Para levantar este proyecto en otro dispositivo, con el estado actual del repositorio, necesitas tener instalado:

- `Git`: para clonar el repositorio.
- `Docker Desktop`: para ejecutar PostgreSQL en contenedor.
- `WSL 2`: revisar en Windows si Docker Desktop lo instalo o lo habilito durante la instalacion, porque suele usarlo como backend.

## Base de datos PostgreSQL

Se dejo preparada una instancia reproducible con la imagen `postgres:15.17-trixie`.

### Variables por defecto

Las variables base estan en `.env.example`:

```env
POSTGRES_DB=wns_challenge
POSTGRES_USER=wns_user
POSTGRES_PASSWORD=wns_password
POSTGRES_PORT=5432
```

Si quieres personalizarlas:

```powershell
Copy-Item .env.example .env
```

## Como levantar la base

1. Descargar la imagen:

   ```powershell
   docker pull postgres:15.17-trixie
   ```

2. Levantar el contenedor:

   ```powershell
   docker compose up -d postgres
   ```

3. Verificar estado:

   ```powershell
   docker compose ps
   ```

4. Verificar tablas creadas:

   ```powershell
   docker compose exec postgres psql -U wns_user -d wns_challenge -c "\dt"
   ```

## Persistencia

- El esquema se crea automaticamente desde `docker/postgres/init/01_schema.sql` cuando el volumen esta vacio.
- Los datos persisten entre reinicios en el volumen `postgres_data`.
- Si clonas el repo en otro equipo, el esquema vuelve a crearse con `docker compose up -d postgres`.

## Reinicializar todo

Si quieres borrar la base y recrearla desde cero:

```powershell
docker compose down -v
docker compose up -d postgres
```

## Conexion local esperada

- Host: `localhost`
- Puerto: `5432`
- Base: `wns_challenge`
- Usuario: `wns_user`
