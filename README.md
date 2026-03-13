# WNS Challenge

Este `README.md` queda enfocado en la estructura del repositorio, el setup tecnico base y el estado actual del procesamiento, persistencia y consulta de datos implementados en Python.

## Estructura actual

- `consigna.md`: enunciado original del desafio.
- `inputs/`: archivos entregados por la consigna.
- `docs/der.png`: diagrama entidad relacion de la base.
- `docker-compose.yml`: servicios Docker para PostgreSQL, scripts Python y API HTTP.
- `docker/python/Dockerfile`: imagen base para ejecutar scripts Python y la API en contenedor.
- `docker/postgres/init/01_schema.sql`: esquema inicial de la base.
- `.dockerignore`: archivos excluidos del contexto de build.
- `requirements.txt`: dependencias Python del proyecto.
- `src/parsers/`: parseo y normalizacion de archivos fuente.
- `src/cli/`: entrypoints para inspeccionar salidas del parser.
- `src/ingest/`: persistencia de datos normalizados en PostgreSQL.
- `src/services/`: logica de negocio que consume PostgreSQL y la API externa permitida por la consigna.
- `src/api/`: capa HTTP para exponer la resolucion de la consigna.
- `src/ingest/db.py`: configuracion y conexion reutilizable a PostgreSQL.
- `src/ingest/productos.py`: upserts reutilizables para categorias, subcategorias y productos.

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
- `psycopg[binary]==3.2.12`
- `fastapi==0.135.1`
- `uvicorn==0.41.0`

## Entorno Python con Docker

Construir la imagen del servicio Python:

```powershell
docker compose build python
```

Luego puedes ejecutar los parsers sin instalar Python ni dependencias en tu maquina:

```powershell
docker compose run --rm python python -m src.cli.inspect_carnes_pescados
docker compose run --rm python python -m src.cli.inspect_verduleria
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
POSTGRES_HOST=localhost
POSTGRES_DB=wns_challenge
POSTGRES_USER=wns_user
POSTGRES_PASSWORD=wns_password
POSTGRES_PORT=5432
CURRENCY_API_URLS=https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/usd.json,https://{date}.currency-api.pages.dev/v1/currencies/usd.json
```

Si quieres personalizarlas:

```powershell
Copy-Item .env.example .env
```

`CURRENCY_API_URLS` acepta una lista separada por comas de endpoints con placeholder `{date}`. El servicio de cotizacion usa el primero como primario y prueba los siguientes como fallback.

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

La insercion en PostgreSQL desde Python esta implementada para `inputs/Carnes y Pescados.xlsx`, `inputs/verduleria.pdf` e `inputs/Recetas.md`.

- El parser real esta en `src/parsers/carnes_pescados.py`.
- El parser real de verduras esta en `src/parsers/verduleria.py`.
- El parser real de recetas esta en `src/parsers/recetas.py`.
- Los CLI de inspeccion estan en `src/cli/inspect_carnes_pescados.py`, `src/cli/inspect_verduleria.py` y `src/cli/inspect_recetas.py`.
- El CLI de cotizacion esta en `src/cli/cotizar_receta.py`.
- La API HTTP se arma en `src/api/app.py` y `src/api/routes.py`.
- La ingesta actual de carnes y pescados se ejecuta desde `src/ingest/carnes_pescados.py`.
- La ingesta actual de verduleria se ejecuta desde `src/ingest/verduleria.py`.
- La ingesta actual de recetas se ejecuta desde `src/ingest/recetas.py`.
- `src/ingest/db.py` centraliza la configuracion y conexion a PostgreSQL.
- `src/ingest/productos.py` centraliza los upserts reutilizables de categorias, subcategorias y productos.
- `src/services/calculator.py` centraliza la logica de cotizacion del plato.
- `src/services/exchange_rate.py` centraliza la consulta de cotizacion USD/ARS.

### Como ejecutar los parsers

Modo local, Excel, salida legible:

```powershell
python -m src.cli.inspect_carnes_pescados
```

Modo local, PDF, salida legible:

```powershell
python -m src.cli.inspect_verduleria
```

Modo local, Markdown de recetas, salida legible:

```powershell
python -m src.cli.inspect_recetas
```

Modo Docker, Excel, salida legible:

```powershell
docker compose run --rm python python -m src.cli.inspect_carnes_pescados
```

Modo Docker, PDF, salida legible:

```powershell
docker compose run --rm python python -m src.cli.inspect_verduleria
```

Modo Docker, Markdown de recetas, salida legible:

```powershell
docker compose run --rm python python -m src.cli.inspect_recetas
```

### Como ejecutar la ingesta actual

Con PostgreSQL levantado, puedes ejecutar la ingesta de carnes y pescados asi:

Modo local:

```powershell
python -m src.ingest.carnes_pescados
```

Modo Docker:

```powershell
docker compose run --rm python python -m src.ingest.carnes_pescados
```

Con PostgreSQL levantado, puedes ejecutar la ingesta de verduleria asi:

Modo local:

```powershell
python -m src.ingest.verduleria
```

Modo Docker:

```powershell
docker compose run --rm python python -m src.ingest.verduleria
```

Con PostgreSQL levantado y con `productos` ya cargados desde Excel y PDF, puedes ejecutar la ingesta de recetas asi:

Modo local:

```powershell
python -m src.ingest.recetas
```

Modo Docker:

```powershell
docker compose run --rm python python -m src.ingest.recetas
```

### Como visualizar lo insertado

Resumen de cantidades:

```powershell
docker compose exec postgres psql -U wns_user -d wns_challenge -c "SELECT COUNT(*) AS categorias FROM categorias; SELECT COUNT(*) AS subcategorias FROM subcategorias; SELECT COUNT(*) AS productos FROM productos;"
```

Categorias y subcategorias cargadas:

```powershell
docker compose exec postgres psql -U wns_user -d wns_challenge -c "SELECT c.nombre AS categoria, s.nombre AS subcategoria FROM subcategorias s JOIN categorias c ON c.id_categoria = s.id_categoria ORDER BY c.nombre, s.nombre;"
```

Productos cargados con su precio:

```powershell
docker compose exec postgres psql -U wns_user -d wns_challenge -c "SELECT c.nombre AS categoria, s.nombre AS subcategoria, p.nombre AS producto, p.precio_kg_ars, p.es_estacional FROM productos p JOIN subcategorias s ON s.id_subcategoria = p.id_subcategoria JOIN categorias c ON c.id_categoria = s.id_categoria ORDER BY c.nombre, s.nombre, p.nombre;"
```

Recetas cargadas:

```powershell
docker compose exec postgres psql -U wns_user -d wns_challenge -c "SELECT id_receta, nombre FROM recetas ORDER BY nombre;"
```

Ingredientes por receta:

```powershell
docker compose exec postgres psql -U wns_user -d wns_challenge -c "SELECT r.nombre AS receta, p.nombre AS producto, ri.cantidad_gramos FROM receta_ingredientes ri JOIN recetas r ON r.id_receta = ri.id_receta JOIN productos p ON p.id_producto = ri.id_producto ORDER BY r.nombre, p.nombre;"
```

Recetas con ingredientes agrupados en una sola fila:

```powershell
docker compose exec postgres psql -U wns_user -d wns_challenge -c "SELECT r.nombre AS receta, STRING_AGG(p.nombre || ' (' || ri.cantidad_gramos::text || ' g)', ', ' ORDER BY p.nombre) AS ingredientes FROM receta_ingredientes ri JOIN recetas r ON r.id_receta = ri.id_receta JOIN productos p ON p.id_producto = ri.id_producto GROUP BY r.id_receta, r.nombre ORDER BY r.nombre;"
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

## Resolver la consigna

Con PostgreSQL levantado y con las tres fuentes ya ingeridas, la aplicacion puede cotizar un plato directamente desde la base.

### 1. Listar recetas disponibles

Modo local:

```powershell
python -m src.cli.cotizar_receta --listar-recetas
```

Modo Docker:

```powershell
docker compose run --rm python python -m src.cli.cotizar_receta --listar-recetas
```

### 2. Cotizar una receta por fecha

La fecha debe estar en formato `YYYY-MM-DD` y dentro de los ultimos 30 dias. El calculo:

- usa los productos ya persistidos en PostgreSQL
- redondea cada compra al siguiente multiplo de `250 g`
- consulta la API de cotizacion historica USD/ARS indicada en la consigna
- permite configurar endpoints alternativos con `CURRENCY_API_URLS` sin tocar el codigo

Modo local:

```powershell
python -m src.cli.cotizar_receta --receta "Asado con ensalada criolla" --fecha YYYY-MM-DD
```

Modo Docker:

```powershell
docker compose run --rm python python -m src.cli.cotizar_receta --receta "Asado con ensalada criolla" --fecha YYYY-MM-DD
```

La salida incluye:

- nombre de la receta
- fecha cotizada
- cotizacion USD/ARS usada
- ingredientes con cantidad pedida, cantidad a comprar, precio por kilo y subtotal
- total final en pesos argentinos y dolares estadounidenses

## API HTTP

Ademas del CLI, la resolucion de la consigna tambien se expone por HTTP.

### Levantar la API en local

```powershell
python -m uvicorn src.api.app:app --reload
```

### Levantar la API con Docker

```powershell
docker compose --profile api up --build api
```

### Endpoints

- `GET /api/health`: verifica que la API este arriba.
- `GET /api/recetas`: devuelve las recetas ya cargadas en PostgreSQL.
- `GET /api/cotizacion?receta=...&fecha=YYYY-MM-DD`: cotiza una receta usando PostgreSQL y la API historica USD/ARS.
- `GET /docs`: documentacion interactiva generada por FastAPI.

### Diagramas de secuencia de la API

`GET /api/health`:

![Diagrama de secuencia health](docs/diagrama-de-secuencia-health.png)

`GET /api/recetas`:

![Diagrama de secuencia recetas](docs/diagrama-de-secuencia-recetas.png)

`GET /api/cotizacion`:

![Diagrama de secuencia cotizacion](docs/diagrama-de-secuencia-cotizacion.png)

Ejemplos locales:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/health"
Invoke-RestMethod "http://127.0.0.1:8000/api/recetas"
Invoke-RestMethod "http://127.0.0.1:8000/api/cotizacion?receta=Asado%20con%20ensalada%20criolla&fecha=YYYY-MM-DD"
```

### Probar endpoints en Postman

1. Probar estas URLs con metodo `GET`:

   - `http://127.0.0.1:8000/api/health`
   - `http://127.0.0.1:8000/api/recetas`
   - `http://127.0.0.1:8000/api/cotizacion?receta=Asado%20con%20ensalada%20criolla&fecha=YYYY-MM-DD`

2. Para cotizar, reemplazar `YYYY-MM-DD` por una fecha valida dentro de los ultimos 30 dias.

3. Si quieres explorar la API visualmente antes de probar en Postman, tambien puedes abrir:

   - `http://127.0.0.1:8000/docs`
