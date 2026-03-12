# WNS Challenge

Este `README.md` queda enfocado en la estructura del repositorio, el setup tecnico base y el estado actual de los parsers implementados en Python.

## Estructura actual

- `consigna.md`: enunciado original del desafio.
- `inputs/`: archivos entregados por la consigna.
- `docs/der.png`: diagrama entidad relacion de la base.
- `docker-compose.yml`: servicio PostgreSQL con Docker.
- `docker/python/Dockerfile`: imagen base para ejecutar parsers de Python en contenedor.
- `docker/postgres/init/01_schema.sql`: esquema inicial de la base.
- `.dockerignore`: archivos excluidos del contexto de build.
- `requirements.txt`: dependencias Python del parser actual.
- `src/parsers/`: parseo y normalizacion de archivos fuente.
- `src/cli/`: entrypoints para inspeccionar salidas del parser.
- `src/ingest/`: adaptacion de datos normalizados para futura ingesta en PostgreSQL.

## DER

![DER de la base de datos](docs/der.png)

## Programas necesarios

Para levantar este proyecto en otro dispositivo, con el estado actual del repositorio, tienes dos caminos:

- `Local`: usar Python instalado en tu maquina.
- `Docker`: encapsular el entorno Python y PostgreSQL en contenedores.

### Opcion local

Necesitas tener instalado:

- `Git`: para clonar el repositorio.
- `Python 3`: para ejecutar el parser y la futura capa de procesamiento.
- `pip`: para instalar dependencias Python.

### Opcion Docker

Necesitas tener instalado:

- `Git`: para clonar el repositorio.
- `Docker Desktop`: para ejecutar PostgreSQL en contenedor.
- `WSL 2`: revisar en Windows si Docker Desktop lo instalo o lo habilito durante la instalacion, porque suele usarlo como backend.

## Entorno Python local

Antes de instalar dependencias, crear un entorno virtual local en el root del proyecto:

```powershell
python -m venv .venv
```

Si trabajas en VS Code, selecciona `.venv\Scripts\python.exe` como interpreter del workspace. Si prefieres activarlo manualmente en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea `Activate.ps1`, no hace falta depender de la activacion manual: basta con seleccionar ese interpreter en VS Code o ejecutar `.\.venv\Scripts\python.exe` directamente.

Luego instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Dependencias actuales:

- `pandas==3.0.1`
- `openpyxl==3.1.5`
- `pdfplumber==0.11.9`

## Entorno Python con Docker

Construir la imagen del servicio Python:

```powershell
docker compose build python
```

Luego puedes ejecutar los parsers sin instalar Python ni dependencias en tu maquina:

```powershell
docker compose run --rm python python -m src.cli.inspect_carnes_pescados
docker compose run --rm python python -m src.cli.inspect_verduleria --json
```

Nota:

- Los comandos `python -m ...` del `README` siguen siendo el camino local.
- Con Docker, los equivalentes pasan a ser `docker compose run --rm python python -m ...`.
- El contenedor monta el repo completo, por eso lee `inputs/` y `src/` directamente desde tu copia local.

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

## Parsers actuales

Por ahora la parte implementada en Python cubre:

- el parseo y la normalizacion de `inputs/Carnes y Pescados.xlsx`
- el parseo y la normalizacion de `inputs/verduleria.pdf`
- el parseo y la normalizacion de `inputs/Recetas.md`

Todavia no esta implementada la insercion en PostgreSQL desde Python.

- El parser real esta en `src/parsers/carnes_pescados.py`.
- El parser real de verduras esta en `src/parsers/verduleria.py`.
- El parser real de recetas esta en `src/parsers/recetas.py`.
- Los CLI de inspeccion estan en `src/cli/inspect_carnes_pescados.py`,  `src/cli/inspect_verduleria.py` y`src/cli/inspect_recetas.py`.
- La capa `src/ingest/` solo prepara payloads para la futura insercion en PostgreSQL.

### Como ejecutar los parsers

Modo local, Excel, salida legible:

```powershell
python -m src.cli.inspect_carnes_pescados
```

Modo local, Excel, salida JSON:

```powershell
python -m src.cli.inspect_carnes_pescados --json
```

Modo local, PDF, salida legible:

```powershell
python -m src.cli.inspect_verduleria
```

Modo local, PDF, salida JSON:

```powershell
python -m src.cli.inspect_verduleria --json
```

Modo local, Markdown de recetas, salida legible:

```powershell
python -m src.cli.inspect_recetas
```

Modo local, Markdown de recetas, salida JSON:

```powershell
python -m src.cli.inspect_recetas --json
```

Modo Docker, Excel, salida legible:

```powershell
docker compose run --rm python python -m src.cli.inspect_carnes_pescados
```

Modo Docker, Excel, salida JSON:

```powershell
docker compose run --rm python python -m src.cli.inspect_carnes_pescados --json
```

Modo Docker, PDF, salida legible:

```powershell
docker compose run --rm python python -m src.cli.inspect_verduleria
```

Modo Docker, PDF, salida JSON:

```powershell
docker compose run --rm python python -m src.cli.inspect_verduleria --json
```

Modo Docker, Markdown de recetas, salida legible:

```powershell
docker compose run --rm python python -m src.cli.inspect_recetas
```

Modo Docker, Markdown de recetas, salida JSON:

```powershell
docker compose run --rm python python -m src.cli.inspect_recetas --json
```

### Salidas normalizadas actuales

El parser del Excel devuelve una lista de productos con esta estructura:

```json
{
  "categoria": "Carniceria",
  "subcategoria": "Carne Vacuna",
  "nombre": "Asado de tira",
  "precio_kg_ars": 6800.0
}
```

El parser del PDF devuelve una lista de productos con esta estructura:

```json
{
  "categoria": "Verduleria",
  "subcategoria": "Fruto",
  "nombre": "Tomate",
  "precio_kg_ars": 1200.0,
  "es_estacional": true
}
```

El parser de recetas devuelve una lista de recetas con esta estructura:

```json
{
  "nombre": "Asado con ensalada criolla",
  "instrucciones": "Cortar las verduras en cubos y mezclarlas con un poco de sal.",
  "ingredientes": [
    {
      "nombre_producto": "Asado de tira",
      "cantidad_gramos": 1000
    }
  ]
}
```

Supuestos actuales del Excel:

- `Carniceria` se toma desde el bloque `C:D` del Excel.
- `Pescaderia` se toma desde el bloque `F:G` del Excel.
- `Pescaderia` no trae subcategoria explicita, por eso se usa `General`.
- Los precios se normalizan desde formatos mixtos como `6800`, `6.000` y `$2600`.

Supuestos actuales del PDF:

- `Verduleria` se toma como categoria unica para todos los productos del PDF.
- La subcategoria se extrae desde lineas como `Fruto por kg`, `Hoja por kg`, `Raiz por kg` y `Tuberculo por kg`.
- `De estacion` se transforma en `es_estacional = true`.
- Las lineas informativas o de pie de pagina no se consideran productos.

Supuestos actuales de `Recetas.md`:

- Cada receta empieza con un encabezado Markdown de nivel 1.
- Las secciones de ingredientes pueden aparecer como `Lista de Ingredientes`, `Ingredientes` o `Lista`.
- Las secciones de instrucciones pueden aparecer como `Instrucciones` o `Preparacion`.
- Las cantidades se normalizan a gramos enteros.
- Los ingredientes quedan referenciados por `nombre_producto` para la futura resolucion contra la tabla `productos`.

### Flujos actuales de los parsers

Excel `Carnes y Pescados.xlsx`:

![Diagrama de flujos carnes y pescados](docs/diagrama-de-flujo-carnes-y-pescados.png)

PDF `verduleria.pdf`:

![Diagrama de flujos verduleria](docs/diagrama-de-flujo-verduleria.png)

Markdown `Recetas.md`:

![Diagrama de flujos recetas](docs/diagrama-de-flujo-recetas.png)
