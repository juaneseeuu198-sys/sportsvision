# 🏋️ SportsVision — Django App

Aplicación web de fitness construida con **Django 4+**, **SQLite** y **Bootstrap 5**.

---

## 📁 Estructura del Proyecto

```
sportsvision/
├── manage.py
├── seed_data.py              ← Script para cargar datos iniciales
├── db.sqlite3                ← Base de datos (se crea al migrar)
│
├── sportsvision/             ← Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── users/                ← Registro, login, dashboard
│   ├── routines/             ← Rutinas, entrenamiento activo
│   ├── exercises/            ← Catálogo de ejercicios
│   ├── tools/                ← Calculadora calorías e IMC
│   └── progress/             ← Calendario de progreso
│
├── templates/
│   ├── base/base.html        ← Layout base con sidebar
│   ├── users/
│   ├── routines/
│   ├── tools/
│   └── progress/
│
└── static/
    ├── css/sportsvision.css
    ├── js/sportsvision.js
    └── images/               ← ← AGREGA TUS IMÁGENES AQUÍ
```

---

## 🚀 Instalación y Setup

### 1. Instalar dependencias

```bash
pip install django pillow
```

### 2. Hacer las migraciones

```bash
cd sportsvision
python manage.py makemigrations users routines exercises tools progress
python manage.py migrate
```

### 3. Cargar datos iniciales (ejercicios, equipos, grupos musculares)

```bash
python seed_data.py
```

### 4. Crear superusuario (para el admin)

```bash
python manage.py createsuperuser
```

### 5. Correr el servidor

```bash
python manage.py runserver
```

Visita: **http://127.0.0.1:8000**

---

## 🖼️ Agregar Imágenes

Las imágenes están marcadas con placeholders `img-slot` en los templates. Para reemplazarlas:

### Imágenes estáticas (logo, fondos, equipos)
Coloca tus archivos en `static/images/` y referencia con:
```html
<img src="{% static 'images/logo.png' %}" alt="Logo SportsVision">
```

### Imágenes de equipos y ejercicios (desde el Admin)
1. Ve a **http://127.0.0.1:8000/admin/**
2. Entra a **Exercises → Equipos** y sube la imagen de cada equipo
3. Entra a **Exercises → Ejercicios** y sube imagen/GIF de cada ejercicio

### Fondos de landing (hero, auth)
En `templates/users/landing.html`, reemplaza el `div.hero-bg-placeholder` con:
```html
<img src="{% static 'images/hero-bg.jpg' %}" alt="" 
     style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0;">
```

---

## 📱 URLs Principales

| URL | Vista |
|-----|-------|
| `/` | Landing page |
| `/usuarios/auth/` | Elegir login/registro |
| `/usuarios/login/` | Iniciar sesión |
| `/usuarios/registro/` | Crear cuenta |
| `/dashboard/` | Dashboard del usuario |
| `/rutinas/nueva/paso1/` | Crear rutina — Paso 1 (equipo) |
| `/rutinas/nueva/paso2/` | Crear rutina — Paso 2 (músculos) |
| `/rutinas/nueva/paso3/` | Crear rutina — Paso 3 (ejercicios) |
| `/rutinas/auto/` | Auto-generador de rutinas |
| `/herramientas/` | Herramientas fitness |
| `/herramientas/calorias/` | Calculadora de calorías |
| `/herramientas/imc/` | Calculadora de IMC |
| `/progreso/` | Calendario de progreso |
| `/admin/` | Panel de administración |

---

## 🔧 Apps Django

| App | Responsabilidad |
|-----|-----------------|
| `users` | Registro, login, logout, dashboard, perfil |
| `exercises` | Catálogo de ejercicios, equipos, grupos musculares |
| `routines` | Flujo 3 pasos, auto-generador, entrenamiento activo, series |
| `tools` | Calculadora Mifflin-St Jeor, calculadora IMC |
| `progress` | Calendario mensual con historial de entrenamientos |

---

## 🎨 Personalización

El tema visual se controla desde `static/css/sportsvision.css` con variables CSS:

```css
:root {
  --sv-bg:           #1a1a2e;   /* Fondo principal */
  --sv-purple:       #7b2ff7;   /* Color acento principal */
  --sv-green:        #00d4aa;   /* Éxito / completado */
  --sv-red:          #e63946;   /* Peligro / eliminar */
}
```
