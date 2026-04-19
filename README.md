<div align="center">
  <img src="assets/MovieFlow.png" alt="MovieFlow Logo">
  <p><strong>Tu flujo continuo hacia el mundo del cine.</strong></p>

  [![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![HTMX](https://img.shields.io/badge/HTMX-v2-336791?style=for-the-badge&logo=htmx&logoColor=white)](https://htmx.org/)
</div>

---

## 🌟 Descripción

**MovieFlow** es una plataforma web moderna y dinámica diseñada para entusiastas del cine. Permite explorar una vasta biblioteca de películas, gestionar créditos de actores y equipo técnico, y participar en una comunidad activa mediante reseñas y comentarios interactivos.

Integrado con la API de **The Movie Database (TMDB)**, MovieFlow ofrece datos actualizados y una experiencia de usuario fluida gracias a la implementación de **HTMX**.

## 🚀 Características Principales

- 🔍 **Exploración Inteligente**: Descubre películas con detalles completos (sinopsis, fecha de estreno, ingresos, presupuestos).
- 👥 **Gestión de Créditos**: Conoce a las personas detrás de las cámaras, desde directores hasta el reparto principal.
- 💬 **Interacción Social**: Deja comentarios y puntúa tus películas favoritas con un sistema de reseñas intuitivo.
- ⚡ **Interfaz Reactiva**: Navegación rápida y actualizaciones sin recargar la página mediante HTMX.
- 🛠️ **Panel de Administración**: Gestión completa de géneros, personas y películas desde el robusto admin de Django.

## 🛠️ Stack Tecnológico

- **Backend:** Django 5.2 (Python 3.10+)
- **Frontend:** HTML5, CSS3, Vanilla JS + [HTMX](https://htmx.org/)
- **Base de Datos:** PostgreSQL
- **Integración:** API de TMDB

## ⚙️ Configuración e Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/MovieFlow.git
cd MovieFlow
```

### 2. Crear un entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia el archivo de ejemplo y edítalo con tus credenciales:
```bash
cp .env-example .env
```
Asegúrate de configurar:
- `SECRET_KEY`
- Credenciales de PostgreSQL
- `API_KEY` y `API_TOKEN` de [TMDB](https://www.themoviedb.org/documentation/api)

### 5. Migraciones y servidor
```bash
python manage.py migrate
python manage.py runserver
```

## 📁 Estructura del Proyecto

- `movies/`: Lógica principal de películas, comentarios y reseñas.
- `users/`: Gestión de perfiles y autenticación.
- `mymovies/`: Configuración global del proyecto Django.
- `templates/`: Archivos HTML divididos por componentes.

---

## 👨‍🏫 Créditos

Este proyecto fue propuesto y guiado por el profesor **Mario Garcia** ([@mariosky](https://github.com/mariosky)), como parte del proceso de aprendizaje en desarrollo web moderno con Django.

---

<div align="center">
  Hecho con ❤️ por el equipo de MovieFlow
</div>
