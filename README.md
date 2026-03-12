# WNS Challenge

Este `README.md` queda enfocado en la estructura del repositorio, el setup tecnico base y el estado actual del parser de `Carnes y Pescados.xlsx`.

## Estructura actual

- `consigna.md`: enunciado original del desafio.
- `inputs/`: archivos entregados por la consigna.
- `docs/der.png`: diagrama entidad relacion de la base.
- `docker-compose.yml`: servicio PostgreSQL con Docker.
- `docker/postgres/init/01_schema.sql`: esquema inicial de la base.
- `requirements.txt`: dependencias Python del parser actual.
- `src/parsers/`: parseo y normalizacion de archivos fuente.
- `src/cli/`: entrypoints para inspeccionar salidas del parser.
- `src/ingest/`: adaptacion de datos normalizados para futura ingesta en PostgreSQL.

## DER

![DER de la base de datos](docs/der.png)

## Programas necesarios

Para levantar este proyecto en otro dispositivo, con el estado actual del repositorio, necesitas tener instalado:

- `Git`: para clonar el repositorio.
- `Python 3`: para ejecutar el parser y la futura capa de procesamiento.
- `pip`: para instalar dependencias Python.
- `Docker Desktop`: para ejecutar PostgreSQL en contenedor.
- `WSL 2`: revisar en Windows si Docker Desktop lo instalo o lo habilito durante la instalacion, porque suele usarlo como backend.

## Dependencias Python

Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Dependencias actuales:

- `pandas==3.0.1`
- `openpyxl==3.1.5`

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

## Parser actual

Por ahora la parte implementada en Python cubre solo el parseo y la normalizacion de `inputs/Carnes y Pescados.xlsx`.

- El parser real esta en `src/parsers/carnes_pescados.py`.
- El CLI de inspeccion esta en `src/cli/inspect_carnes_pescados.py`.
- La capa `src/ingest/carnes_pescados.py` solo prepara el payload para la futura insercion en PostgreSQL.
- Todavia no se insertan datos en la base desde Python.

### Como ejecutar el parser

Salida legible:

```powershell
python -m src.cli.inspect_carnes_pescados
```

Salida JSON:

```powershell
python -m src.cli.inspect_carnes_pescados --json
```

### Salida normalizada actual

El parser devuelve una lista de productos con esta estructura:

```json
{
  "categoria": "Carniceria",
  "subcategoria": "Carne Vacuna",
  "nombre": "Asado de tira",
  "precio_kg_ars": 6800.0
}
```

Supuestos actuales:

- `Carniceria` se toma desde el bloque `C:D` del Excel.
- `Pescaderia` se toma desde el bloque `F:G` del Excel.
- `Pescaderia` no trae subcategoria explicita, por eso se usa `General`.
- Los precios se normalizan desde formatos mixtos como `6800`, `6.000` y `$2600`.

### Flujo actual del parser

![Diagrama de flujos carnes y pescados](docs/diagrama-de-flujo-carnes-y-pescados.png)
