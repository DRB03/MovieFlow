import os
import environ
import requests
import psycopg2
from datetime import datetime, date, timezone 
import sys
import time

def add_movie(movie_id):
    env = environ.Env()
    environ.Env.read_env('.env')
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {env('API_TOKEN')}"
    }

    # 1. Obtener detalles de la película
    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?language=en-US', headers=headers) 
    m = r.json()

    # Si la API devuelve un error (ej. ID no válido), detenemos esta iteración
    if 'title' not in m:
        print(f"No se pudo encontrar la película con ID {movie_id}")
        return

    conn = psycopg2.connect(dbname='django', host='/tmp')
    cur = conn.cursor()

    # Verificar si ya existe para no duplicar
    sql = 'SELECT * FROM movies_movie WHERE title = %s'
    cur.execute(sql, (m['title'],))
    if cur.fetchall():
        print(f"La película '{m['title']}' ya existe en la base de datos. Saltando...")
        return

    # 2. Obtener créditos
    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US', headers=headers) 
    credits = r.json()

    actors = [(actor['name'], actor['known_for_department']) for actor in credits.get('cast', [])[:10]] 
    crew = [(job['name'], job['job']) for job in credits.get('crew', [])[:15]]
    credits_list = actors + crew

    # Insertar Trabajos (Jobs)
    jobs = set([job for person, job in credits_list])
    if jobs:
        sql = 'SELECT * FROM movies_job WHERE name IN %s'
        cur.execute(sql, (tuple(jobs),))
        jobs_in_db = [name for id, name in cur.fetchall()]
        jobs_to_create = [(name,) for name in jobs if name not in jobs_in_db]
        if jobs_to_create:
            sql = 'INSERT INTO movies_job (name) values (%s)'
            cur.executemany(sql, jobs_to_create) 

    # Insertar Personas (Persons)
    persons = set([person for person, job in credits_list])
    if persons:
        sql = 'SELECT * FROM movies_person WHERE name IN %s'
        cur.execute(sql, (tuple(persons),))
        persons_in_db = [name for id, name in cur.fetchall()]
        persons_to_create = [(name,) for name in persons if name not in persons_in_db]
        if persons_to_create:
            sql = 'INSERT INTO movies_person (name) values (%s)'
            cur.executemany(sql, persons_to_create) 

    # Insertar Géneros (Genres)
    genres = [d['name'] for d in m.get('genres', [])] 
    if genres:
        sql = 'SELECT * FROM movies_genre WHERE name IN %s'
        cur.execute(sql, (tuple(genres),))
        genres_in_db = [name for id, name in cur.fetchall()]
        genres_to_create = [(name,) for name in genres if name not in genres_in_db]
        if genres_to_create:
            sql = 'INSERT INTO movies_genre (name) values (%s)'
            cur.executemany(sql, genres_to_create) 

    # Insertar Película
    date_obj = date.fromisoformat(m['release_date']) if m.get('release_date') else date.today()
    date_time = datetime.combine(date_obj, datetime.min.time())

    sql = '''INSERT INTO movies_movie 
             (title, overview, release_date, running_time, budget, tmdb_id, revenue, poster_path) 
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'''
             
    movie_tuple = (m['title'], m.get('overview', ''), date_time.astimezone(timezone.utc), 
                   m.get('runtime', 0), m.get('budget', 0), movie_id, 
                   m.get('revenue', 0), m.get('poster_path', ''))
    
    cur.execute(sql, movie_tuple)

    # Relacionar Película con Géneros
    if genres:
        sql = '''INSERT INTO movies_movie_genres (movie_id, genre_id)
                 SELECT (SELECT id FROM movies_movie WHERE title = %s) as movie_id, id as genre_id 
                 FROM movies_genre 
                 WHERE name IN %s'''
        cur.execute(sql, (m['title'], tuple(genres),))

    # Relacionar Película con Créditos (Personas y Trabajos)
    for credit in credits_list:
        sql = '''INSERT INTO movies_moviecredit (movie_id, person_id, job_id)
                 SELECT id,
                 (SELECT id FROM movies_person WHERE name = %s LIMIT 1) as person_id,
                 (SELECT id FROM movies_job WHERE name = %s LIMIT 1) as job_id
                 FROM movies_movie 
                 WHERE title = %s'''
        cur.execute(sql, (credit[0], credit[1], m['title'],))

    conn.commit()
    print(f"¡Éxito! Se guardó '{m['title']}' en la base de datos.")


def load_multiple_movies(pages=2):
    """
    Obtiene las películas más populares de TMDB y las guarda en la base de datos.
    pages=2 traerá 40 películas (20 por página).
    """
    env = environ.Env()
    environ.Env.read_env('.env')
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {env('API_TOKEN')}"
    }

    movie_ids = []
    
    # 1. Extraer los IDs de las páginas populares
    for page in range(1, pages + 1):
        print(f"Obteniendo página {page} de películas populares...")
        url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            for movie in data.get('results', []):
                movie_ids.append(movie['id'])
        else:
            print(f"Error al contactar la API en la página {page}")

    print(f"\nSe encontraron {len(movie_ids)} películas para procesar.\n")

    # 2. Insertar cada película en la base de datos
    for index, m_id in enumerate(movie_ids, 1):
        print(f"[{index}/{len(movie_ids)}] Procesando ID: {m_id}...")
        try:
            add_movie(m_id)
            # Pausa de medio segundo para no saturar la API de TMDB ni tu base de datos
            time.sleep(0.5) 
        except Exception as e:
            print(f"Hubo un error con el ID {m_id}: {e}")

if __name__ == "__main__":
    # Ejecutamos la función para traer 2 páginas (40 películas)
    load_multiple_movies(pages=2)
