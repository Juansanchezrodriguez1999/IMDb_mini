# IMDb Data Platform

Plataforma completa y production-ready diseñada para permitir a los clientes consultar información de IMDb (personas y películas) a través de una **API REST** (FastAPI), un **proceso ETL** automatizado y una **interfaz web** intuitiva.

El proyecto implementa una arquitectura **cliente-servidor escalable** que proporciona acceso de manera amigable a la base de datos de IMDb mediante endpoints REST bien documentados y una interfaz de usuario intuitiva.

## Características principales

- **ETL Automatizado**: Descarga e ingesta automática de datasets públicos de IMDb desde `https://datasets.imdbws.com`
- **API REST**: API FastAPI con endpoints específicos para consultar información sobre personas y películas
- **Frontend web**: Interfaz intuitiva para búsquedas avanzadas y visualización de resultados
- **Base de datos PostgreSQL**: Esquema optimizado para queries de alta performance
- **Docker Compose**: Orquestación completa y automatizada de todos los servicios
- **PgAdmin integrado**: Panel de administración para inspeccionar y gestionar la base de datos
- **Production-ready**: Unit tests, logging detallado, mantenibilidad y documentación exhaustiva

---

## Requisitos previos

- Docker (https://www.docker.com)
- Docker Compose 
- Conexión a Internet 
- Mínimo 2 GB de espacio disponible para la base de datos

---

## Inicio rápido

### 0. Creación de la red Docker

Antes de levantar cualquier servicio, es necesario crear la red Docker compartida que será utilizada por todos los contenedores:

```bash
docker network create app-network
```

**Nota importante**: Este comando debe ejecutarse una sola vez. Si la red ya existe, Docker ignorará el comando sin mostrar errores.

Para verificar que la red ha sido creada correctamente, ejecutar:

```bash
docker network ls
```

El resultado debe incluir una línea con `app-network` en la lista de redes disponibles.

### 1. Levantar los servicios de base de datos

Desde el directorio raíz del proyecto, ejecutar:

```bash
cd bbdd
docker compose up --build -d
cd ..
```

Este paso inicializa:
- **PostgreSQL**: Base de datos relacional en `localhost:5432`
- **PgAdmin**: Panel de administración de base de datos en `http://localhost:8080`
  - Usuario: `admin@example.com`
  - Contraseña: `admin`

Para verificar que PostgreSQL ha iniciado correctamente, ejecutar:

```bash
docker compose logs postgres
```

### 2. Levantar los servicios de ETL, API y Frontend

Desde el directorio raíz del proyecto:

```bash
docker compose up --build
```

Este comando inicia de manera paralela los siguientes servicios:
- **ETL** (`imdb_etl`): Proceso de descarga e ingesta de datos de IMDb en PostgreSQL
- **FastAPI** (`imdb_fastapi`): Servidor API REST disponible en `http://localhost:8000`
- **Frontend** (`frontend`): Interfaz web disponible en `http://127.0.0.1:5000/`


### 3. Verificación de disponibilidad de servicios

Una vez que todos los servicios están en ejecución, acceder a los siguientes endpoints para verificar funcionalidad:

- **Frontend**: `http://127.0.0.1:5000/`
- **API Swagger**: `http://localhost:8000/docs`
- **PgAdmin (administración de BD)**: `http://localhost:8080`

---

## Gestión de servicios

### Detener servicios sin eliminar datos

Para detener la ejecución de los servicios preservando los datos almacenados en la base de datos:

```bash
# Detener ETL, API y Frontend
docker compose down

# Detener servicios de BD
cd bbdd
docker compose down
cd ..
```

## Configuración de variables de entorno

### Variables globales (`.env` en directorio raíz)

El archivo `.env` en el directorio raíz contiene las variables de entorno compartidas por todos los servicios:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
API_URL=http://fastapi:8000
ETL_DOWNLOAD_DIR=/data
```

**Consideraciones importantes**:
- `POSTGRES_HOST=postgres` debe coincidir exactamente con el nombre del servicio definido en `bbdd/docker-compose.yml`
- `POSTGRES_PORT=5432` representa el puerto interno de Docker (diferente del puerto mapeado en el host)
- `ETL_DOWNLOAD_DIR=/data` especifica el directorio donde el módulo ETL almacena los archivos descargados

---

## Uso del sistema

### API REST (FastAPI)

La API está disponible en la dirección **`http://localhost:8000`**

#### Acceso a documentación interactiva

La documentación Swagger UI está disponible en:

```
http://localhost:8000/docs
```

#### Endpoints disponibles

**Endpoint de búsqueda de personas**

```http
GET /people?name=Bruce%20Lee
```

**Estructura de respuesta esperada**:

```json
{
  "id": "nm0000075",
  "primary_name": "Bruce Lee",
  "birth_year": 1940,
  "death_year": 1973,
  "primary_profession": ["actor", "film_producer", "martial_artist"],
  "summary": "Bruce Lee fue un actor, productor de películas y artista marcial nacido en 1940 y fallecido en 1973."
}
```

**Endpoint de búsqueda de películas**

```http
GET /titles?title=Blacksmith
```

**Estructura de respuesta esperada**:

```json
{
  "id": "tt0000005",
  "title_type": "short",
  "primary_title": "Blacksmith Scene",
  "original_title": "Les forgerons",
  "start_year": 1893,
  "runtime_minutes": 1,
  "genres": ["Documentary", "Short"],
  "summary": "Blacksmith Scene, titulado originalmente como 'Les forgerons', es un cortometraje documental producido en 1893."
}
```

### Frontend (interfaz web)

La interfaz web está disponible en **`http://127.0.0.1:5000/`**

**Flujo típico de uso**:

1. El usuario accede a la página principal (`http://127.0.0.1:5000/`)
2. Selecciona el tipo de búsqueda: "Persona" o "Película"
3. Introduce los términos de búsqueda en el campo proporcionado
4. Envía la solicitud mediante Enter o haciendo clic en el botón "Buscar"
5. El frontend realiza una llamada HTTP a la API FastAPI
6. El sistema retorna y presenta:
   - **Listado de resultados**: tabla con todos los elementos coincidentes
   - **Vista detallada**: información completa al hacer clic en un resultado específico

### PgAdmin (administración de base de datos)

La herramienta de administración de base de datos está disponible en **`http://localhost:8080`**

**Credenciales de acceso**:
- Usuario: `admin@example.com`
- Contraseña: `admin`

**Pasos para conectar a la base de datos de IMDb**:

1. Hacer clic derecho en "Servers" → New → Server
2. En la sección "General": asignar el nombre "IMDb"
3. En la sección "Connection":
   - Host: `postgres`
   - Puerto: `5432`
   - Nombre de usuario: `user`
   - Contraseña: `password`
   - Base de datos: `db`
4. Guardar la configuración

---

## Descripción de módulos

### Módulo 1: ETL (`etl/`)

**Propósito**: Automatizar la ingesta de datos públicos de IMDb en la base de datos relacional.

**Archivo principal**: `etl/etl.py`

**Proceso de ejecución**:

1. Descarga archivos TSV comprimidos desde `https://datasets.imdbws.com`:
   - `name.basics.tsv.gz`
   - `title.basics.tsv.gz`
   - `title.principals.tsv.gz`
   - `title.ratings.tsv.gz`
2. Descomprime los archivos y realiza parsing de los datos
3. Aplica transformaciones y procedimientos de limpieza
4. Realiza inserción en PostgreSQL


### Módulo 2a: API REST (`fastapi/`)


**Endpoints disponibles**:

- `GET /people?name=<str>` — Busca personas por nombre (búsqueda parcial)
- `GET /titles?title=<str>` — Busca películas por título (búsqueda parcial)
- `GET /docs` — Documentación interactiva Swagger UI

### Módulo 2b: Frontend (`frontend/`)

**Framework utilizado**: Flask + HTML/CSS/JavaScript

**Estructura de archivos**:

- `app.py` — Rutas Flask, gestión de sesiones y llamadas al API FastAPI
- `templates/base.html` — Plantilla base con navegación y estilos globales
- `templates/index.html` — Formulario principal de búsqueda
- `templates/results_people.html` — Tabla de resultados para búsqueda de personas
- `templates/person_detail.html` — Página de detalle de persona específica
- `templates/results_titles.html` — Tabla de resultados para búsqueda de películas
- `templates/title_detail.html` — Página de detalle de película específica

**Rutas principales**:

- `GET /` — Página de inicio con formulario de búsqueda
- `POST /search` — Procesamiento de búsquedas de personas o películas
- `GET /person/<id>` — Visualización de información detallada de persona
- `GET /title/<id>` — Visualización de información detallada de película

---

## Testing y validación

### Estructura de tests

El proyecto incluye una suite completa de tests unitarios organizados en la carpeta `tests/` con cobertura para los tres módulos principales:

- `test_etl.py` — Tests del módulo ETL
- `test_fastapi.py` — Tests de la API REST
- `test_frontend.py` — Tests del frontend Flask

### Configuración de dependencias

Para ejecutar los tests, instalar las dependencias necesarias desde `tests/requirements.txt`:

```bash
cd tests
pip install -r requirements.txt
cd ..
```

Las dependencias incluyen:
- `pytest` — Framework de testing
- `pytest-cov` — Cobertura de código
- `requests-mock` — Mock de requests HTTP
- `Flask` — Cliente de testing para Flask

### Ejecución de pruebas

#### Ejecutar todos los tests

Desde el directorio raíz del proyecto:

```bash
python -m pytest -v
```

#### Ejecutar tests específicos por módulo

**Tests del módulo ETL**:

```bash
python -m pytest tests/test_etl.py -v
```

**Tests de la API FastAPI**:

```bash
python -m pytest tests/test_fastapi.py -v
```

**Tests del frontend Flask**:

```bash
python -m pytest tests/test_frontend.py -v
```

#### Ejecutar un test individual

```bash
python -m pytest tests/test_etl.py::test_download_and_extract_skip_if_exists -v
```

---

## Mantenimiento y operación

### Recarga de datos de IMDb

En caso de necesidad de actualizar los datos a una versión más reciente de IMDb:

```bash
# 1. Detener todos los servicios
docker compose down
cd bbdd
docker compose down
cd ..

# 2. Eliminar volumen de base de datos (elimina permanentemente los datos)
docker volume rm imdb_postgres_data

# 3. Relanzar los servicios para reinicializar
cd bbdd
docker compose up --build -d
cd ..
docker compose up --build
```

### Adición de nuevos endpoints

Para agregar nuevos endpoints a la API:

1. Crear o editar archivos en `fastapi/app/controllers/`
2. Definir nuevas rutas siguiendo la estructura existente
3. Registrar el nuevo router en `fastapi/app/main.py`
4. Reiniciar el contenedor o usar flag `--reload` en desarrollo

### Extensión del esquema de base de datos

Para agregar nuevas tablas o columnas:

1. Editar `bbdd/init/01_imdb_schema.sql` con los cambios necesarios
2. Opcionalmente: eliminar el volumen existente de PostgreSQL
3. Relanzar los contenedores para aplicar cambios (ejecutar scripts de inicialización)

### Modificación de configuración

Para cambiar parámetros de configuración:

1. Editar archivos `.env` (raíz y/o específicos de servicio)
2. Detener servicios actuales: `docker compose down`
3. Relanzar servicios: `docker compose up`

---

## Trabajo futuro

Como posible evolución del proyecto, se plantea la incorporación de **técnicas de Inteligencia Artificial** orientadas a enriquecer la experiencia de búsqueda y mejorar el rendimiento de las consultas, especialmente en escenarios con grandes volúmenes de datos y búsquedas semánticas complejas.

### Búsqueda semántica mediante vectorización

Actualmente, las búsquedas se basan principalmente en coincidencias parciales de texto sobre campos estructurados. Como mejora futura, se propone la **vectorización de la información textual relevante** (por ejemplo, nombres, descripciones, profesiones, géneros y resúmenes) utilizando modelos de *embeddings* de lenguaje natural.

Mediante este enfoque, cada entidad (persona o película) se transformaría en un **vector numérico de alta dimensión** que representa su significado semántico. De forma análoga, las consultas de los usuarios también podrían vectorizarse, permitiendo realizar búsquedas por **similitud semántica** en lugar de depender exclusivamente de coincidencias literales.

Esto permitiría, por ejemplo:
- Encontrar resultados relevantes aunque la consulta no coincida exactamente con el texto almacenado
- Gestionar mejor sinónimos, variaciones lingüísticas o errores tipográficos
- Ofrecer resultados más contextuales y precisos

### Uso de una base de datos vectorial

Los vectores generados podrían almacenarse en una **base de datos vectorial especializada**, optimizada para realizar búsquedas eficientes de vecinos más cercanos (*nearest neighbor search*). Este tipo de almacenamiento permite ejecutar consultas de similitud de forma mucho más rápida que una búsqueda tradicional sobre grandes volúmenes de texto.

La integración de una base de datos vectorial permitiría:
- Reducir significativamente los tiempos de respuesta en consultas complejas
- Escalar el sistema de manera más eficiente ante un crecimiento del dataset
- Combinar búsquedas semánticas con filtros estructurados (por ejemplo, año, género o tipo de título)

### Integración con la arquitectura actual

Desde el punto de vista arquitectónico, esta mejora podría integrarse de forma natural en el sistema existente:
- El **proceso ETL** se encargaría de generar y actualizar los vectores durante la ingesta de datos
- La **API REST** ampliaría sus endpoints para soportar búsquedas semánticas
- El sistema podría decidir dinámicamente entre consultas relacionales tradicionales y consultas vectoriales, según el tipo de búsqueda solicitada
