import sqlite3
import aiohttp
import asyncio

class MovieDatabase:
    
    #singleton
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MovieDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='KguiDatabase.db'):
        if not hasattr(self, '_initialized'): 
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.setup_databases()
            self._initialized = True

    def setup_databases(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT,
        genre INTEGER,
        language TEXT,
        release_date TEXT,
        popularity REAL,
        vote_average REAL,
        vote_count INTEGER
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY,
        name TEXT
        )
        ''')
        self.conn.commit()

    async def fetch_and_save_genres(self):
        url = "https://api.themoviedb.org/3/genre/movie/list?language=en"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzUxYjg4NTA2M2RiZTU5MWRiZmQ1ZDNjMDVkMzkwZCIsInN1YiI6IjY2NjVhZjY0Y2Y1MmFkYjFhY2UwY2NjMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EDGBOOnxL6CnsRCpxfIDZNEWwRFyCcqbDDPM49sLHDE"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if data.get("genres"):
                    self.cursor.execute('DELETE FROM genres')  # Clear the table
                    self.cursor.executemany('''
                        INSERT INTO genres (id, name) 
                        VALUES (?, ?)
                        ''', [
                        (genre["id"], genre["name"])
                        for genre in data["genres"]
                    ])
                    self.conn.commit()
                print("Genres fetched and saved to database.")

    async def fetch_movies(self, session, url, headers, params):
        async with session.get(url, headers=headers, params=params) as response:
            return await response.json()

    async def fetch_and_save_data(self, title, genre, language, release_date_from, release_date_to):
        url = "https://api.themoviedb.org/3/discover/movie"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjYzUxYjg4NTA2M2RiZTU5MWRiZmQ1ZDNjMDVkMzkwZCIsInN1YiI6IjY2NjVhZjY0Y2Y1MmFkYjFhY2UwY2NjMSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.EDGBOOnxL6CnsRCpxfIDZNEWwRFyCcqbDDPM49sLHDE"
        }

        async with aiohttp.ClientSession() as session:
            # Fetch the first page to get the total number of pages
            params = {
                "include_adult": "false",
                "include_video": "false",
                "language": "en-US",
                "page": 1,
                "sort_by": "popularity.desc"
            }

            if genre:
                params["with_genres"] = genre
            if language:
                params["with_original_language"] = language
            if release_date_from:
                params["primary_release_date.gte"] = release_date_from
            if release_date_to:
                params["primary_release_date.lte"] = release_date_to

            first_page_data = await self.fetch_movies(session, url, headers, params)
            total_pages = first_page_data.get("total_pages", 1)
            all_results = first_page_data.get("results", [])

            # Prepare a list of tasks to fetch remaining pages concurrently
            tasks = []
            for page in range(2, total_pages + 1):
                page_params = {
                    "include_adult": "false",
                    "include_video": "false",
                    "language": "en-US",
                    "page": page,
                    "sort_by": "popularity.desc"
                }

                if genre:
                    page_params["with_genres"] = genre
                if language:
                    page_params["with_original_language"] = language
                if release_date_from:
                    page_params["primary_release_date.gte"] = release_date_from
                if release_date_to:
                    page_params["primary_release_date.lte"] = release_date_to

                tasks.append(self.fetch_movies(session, url, headers, page_params))

            # Await all the tasks and collect results
            pages_data = await asyncio.gather(*tasks)
            for page_data in pages_data:
                all_results.extend(page_data.get("results", []))

            # If a title is provided, filter the results for exact match
            if title:
                all_results = [movie for movie in all_results if movie["title"].lower() == title.lower()]

            # Refresh table and insert movies into the table
            self.cursor.execute('DELETE FROM movies')
            self.cursor.executemany('''
                INSERT INTO movies (id, title, genre, language, release_date, popularity, vote_average, vote_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', [
                (
                    index + 1, #Using index instead of IDs, because API movie ID is not unique
                    movie["title"],
                    movie["genre_ids"][0] if movie["genre_ids"] else None,
                    movie["original_language"],
                    movie["release_date"] if "release_date" in movie else None,
                    movie["popularity"],
                    movie["vote_average"],
                    movie["vote_count"]
                ) for index, movie in enumerate(all_results) if "genre_ids" in movie and movie["genre_ids"]
            ])
            self.conn.commit()
        print("Movies fetched and saved to database.")

    def get_movies(self):
        self.cursor.execute('SELECT * FROM movies ORDER BY title ASC')
        return self.cursor.fetchall()
    
    def get_movies_popularity(self, top_n=15):
        self.cursor.execute('SELECT title, popularity FROM movies ORDER BY popularity DESC LIMIT ?', (top_n,))
        return self.cursor.fetchall()
    
    def get_movies_vote_count(self, top_n=3):
        self.cursor.execute('SELECT title, vote_count FROM movies ORDER BY vote_count DESC LIMIT ?', (top_n,))
        return self.cursor.fetchall()
    
    def get_movies_vote_average(self, top_n=3):
        self.cursor.execute('SELECT title, vote_average FROM movies ORDER BY vote_average DESC LIMIT ?', (top_n,))
        return self.cursor.fetchall()
    
    def get_top_genres(self, top_n=3):
        self.cursor.execute('''
        SELECT genres.name, COUNT(movies.genre) as count
        FROM movies
        JOIN genres ON movies.genre = genres.id
        GROUP BY genres.name
        ORDER BY count DESC
        LIMIT ?
        ''', (top_n,))
        return self.cursor.fetchall()