# Asistente Nutricional Inteligente

## 📋 Descripción

Alana es una aplicación web que utiliza inteligencia artificial para analizar fotos de comida y proporcionar un desglose nutricional detallado. Los usuarios pueden subir fotos de sus comidas, recibir un análisis automático de ingredientes y calorías, y luego ajustar los resultados mediante un chat interactivo con IA para obtener un análisis más preciso.

## ✨ Características

- **Análisis de imágenes**: Identifica los alimentos en una foto y estima sus valores nutricionales
- **Estimación calórica**: Calcula las calorías totales del plato fotografiado
- **Chat interactivo**: Permite a los usuarios refinar los resultados a través de un chat con IA
- **Autenticación**: Sistema completo de registro e inicio de sesión
- **Guardado de análisis**: Almacena los análisis originales y ajustados para referencia futura

## 🏗️ Arquitectura

El proyecto sigue una arquitectura limpia y modular:

```
app/
├── __init__.py        # Factory de la aplicación
├── main.py            # Punto de entrada principal
├── config.py          # Configuración centralizada
├── api/               # API endpoints
│   ├── routes/        # Rutas de la API
│   │   ├── auth.py    # Autenticación
│   │   ├── food.py    # Análisis de comida
│   │   └── chat.py    # Chat interactivo
│   └── dependencies.py # Dependencias de FastAPI
├── core/              # Componentes centrales
│   ├── security.py    # Autenticación y seguridad
│   └── utils.py       # Utilidades generales
├── db/                # Capa de datos
│   ├── database.py    # Configuración de la base de datos
│   └── repositories.py # Operaciones de base de datos
├── models/            # Modelos de datos
│   └── schemas.py     # Esquemas SQLModel y Pydantic
├── ai/                # Componentes de IA
│   ├── prompts.py     # Prompts para modelos de IA
│   ├── vision.py      # Análisis de imágenes
│   └── chatbot.py     # Configuración del chatbot
├── services/          # Lógica de negocio
│   ├── food_service.py # Servicio de análisis de comida
│   └── chat_service.py # Servicio de chat
└── static/            # Frontend
    ├── index.html     # Página principal
    ├── script.js      # JavaScript del cliente
    └── style.css      # Estilos CSS
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.9+
- pip
- Una cuenta de OpenAI con API key

### Pasos

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/alana-app.git
   cd alana-app
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   pip install -r requirements.txt
   ```

3. Crea un archivo `.env` en la raíz del proyecto:
   ```
   OPENAI_API_KEY=tu_api_key_de_openai
   SECRET_KEY=una_clave_secreta_para_tokens_jwt
   ```

4. Ejecuta la aplicación:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Accede a la aplicación en tu navegador: `http://localhost:8000`

## 📦 Dependencias principales

- **FastAPI**: Framework web de alto rendimiento
- **SQLModel**: ORM para trabajar con bases de datos SQL
- **OpenAI**: Para análisis de imágenes y chat con IA
- **Pydantic**: Validación de datos
- **Jose**: Manejo de JWT para autenticación
- **LangGraph**: Para crear flujos de conversación con IA

## 📝 Uso

1. **Registro/Inicio de sesión**:
   - Crea una cuenta o inicia sesión con email y contraseña

2. **Análisis de comida**:
   - Toma una foto de tu comida o sube una imagen
   - Espera mientras la IA analiza la imagen
   - Recibe un desglose detallado de ingredientes y calorías

3. **Ajuste del análisis**:
   - Usa el chat para corregir cualquier detalle
   - Ejemplo: "El arroz es integral, no blanco" o "Usé aceite de oliva extra virgen"
   - La IA actualizará el análisis nutricional

4. **Guardado**:
   - Guarda el análisis para revisarlo más tarde

## 🧩 Estructura de módulos

### API

Los endpoints de la API están organizados por funcionalidad:

- **auth.py**: Maneja el registro y autenticación
- **food.py**: Procesa imágenes de comida
- **chat.py**: Maneja la conversación para ajustes

### Base de datos

- **database.py**: Configura la conexión a la base de datos
- **repositories.py**: Implementa el patrón repositorio para acceder a los datos

### Modelos

- **schemas.py**: Define modelos para la base de datos y validación

### IA

- **prompts.py**: Define los prompts para los modelos de IA
- **vision.py**: Implementa el análisis de imágenes
- **chatbot.py**: Configura el chatbot interactivo

### Servicios

- **food_service.py**: Lógica para análisis de comida
- **chat_service.py**: Lógica para el chat interactivo

## 🧪 Pruebas

Ejecuta las pruebas con:

```bash
pytest
```

## 🚧 Desarrollo

1. Asegúrate de seguir las guías de estilo:
   ```bash
   black .
   isort .
   flake8
   ```

2. Añade pruebas para nuevas características

3. Actualiza la documentación según corresponda

## 📱 Frontend

La interfaz de usuario es una SPA (Single Page Application) desarrollada con HTML, JavaScript y TailwindCSS. Proporciona:

- Diseño responsive para móviles y escritorio
- Interfaz moderna y amigable
- Experiencia de usuario fluida

## 🔄 Flujo de la aplicación

1. El usuario se registra o inicia sesión
2. Sube una foto de su comida
3. La IA analiza la imagen y devuelve un análisis
4. El usuario puede chatear con la IA para ajustar el resultado
5. El resultado final se guarda en la base de datos

## 🔐 Seguridad

- Autenticación JWT
- Passwords hasheadas con bcrypt
- CORS configurado (ajustar para producción)

## 📈 Escalabilidad

Para escalar la aplicación:

- Migrar a PostgreSQL para la base de datos
- Implementar caché con Redis
- Utilizar contenedores Docker para el despliegue
- Configurar un balanceador de carga