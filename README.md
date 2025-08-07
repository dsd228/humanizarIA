# HumanizarIA · Herramientas

Sitio web con herramientas de IA con enfoque ético y humanizado que incluye un backend Flask funcional.

## 🚀 ¿Qué es esto?

Esta web incluye utilidades para experimentar con inteligencia artificial en entornos humanos:
- **Frontend completo**: Interfaz web con Bootstrap 5 y múltiples herramientas
- **Backend Flask**: API REST para humanización y resumen de texto
- **Demo básico**: Versión simplificada siguiendo el patrón del problema inicial

## 📦 Estructura del proyecto

```
humanizarIA/
├── app.py              # Backend Flask con endpoints /humanize y /summary
├── requirements.txt    # Dependencias Python (Flask, flask-cors)
├── index.html         # Frontend completo con múltiples herramientas
├── demo.html          # Demo básico (solo humanizar y resumir)
├── assets/
│   ├── css/styles.css # Estilos personalizados
│   └── js/scripts.js  # JavaScript actualizado para conectar con Flask
└── README.md          # Este archivo
```

## 🛠️ Cómo probarlo localmente

### 1. Configurar el backend

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor Flask
python app.py
```

El backend estará disponible en `http://localhost:5000`

### 2. Abrir el frontend

Opción A - **Demo básico**:
```bash
# Servir archivos estáticos
python -m http.server 8000
# Luego abrir http://localhost:8000/demo.html
```

Opción B - **Interfaz completa**:
```bash
# Abrir http://localhost:8000/index.html
# o directamente abrir index.html en el navegador
```

### 3. Probar las funciones

- **Humanizar**: Ingresa texto y presiona "Humanizar" 
- **Resumir**: Ingresa texto y presiona "Resumir"

## 🌐 Despliegue en producción

### Backend
1. Sube el backend a un hosting que soporte Flask (Render, Heroku, PythonAnywhere, etc.)
2. Actualiza `backendUrl` en los archivos JavaScript para apuntar a tu URL de producción

### Frontend  
1. Actualiza la variable `backendUrl` en `assets/js/scripts.js` y `demo.html`
2. Sube los archivos a GitHub Pages, Netlify o similar
3. Asegúrate de que el backend tenga CORS configurado para tu dominio

## 🔧 API Endpoints

### POST /humanize
```json
{
  "texto": "Texto a humanizar"
}
```

Respuesta:
```json
{
  "humanizado": "Hola! Aquí tienes tu texto humanizado:\n\nTexto a humanizar"  
}
```

### POST /summary
```json
{
  "texto": "Texto largo para resumir..."
}
```

Respuesta:
```json
{
  "resumen": "Primeros 100 caracteres del texto..."
}
```

## 📋 Características

### Frontend Completo (index.html)
- ✅ Humanización de texto con backend Flask
- ✅ Resumen de texto con backend Flask  
- ✅ Extracción de palabras clave (simulado)
- ✅ Análisis de sentimiento (simulado)
- ✅ Interfaz para PDF (placeholder)
- ✅ Captura de pantalla (simulado)
- ✅ Sistema de mensajes y notificaciones
- ✅ Diseño responsive con Bootstrap 5

### Demo Básico (demo.html)
- ✅ Solo humanización y resumen
- ✅ Conectado al backend Flask
- ✅ Interfaz minimalista

### Backend Flask (app.py)
- ✅ Endpoint /humanize funcional
- ✅ Endpoint /summary funcional  
- ✅ CORS habilitado
- ✅ Manejo de errores básico
