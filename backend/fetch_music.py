import requests #External library (installed via pip). Used to make HTTP calls to external APIs — in our case the iTunes API. Without it we can't call any web service.
import pymysql #External library (installed via pip). Used to connect to and interact with MariaDB. Without it we can't run SQL queries or store data in the database.
import sys #Built-in Python module — no installation needed. We use it specifically for sys.argv to read the artist name you type in the terminal when running the script.
import os #Built-in Python module — no installation needed. Used to read environment variables with os.getenv(). In our script we use it to get the database connection details like DB_HOST, DB_PORT, DB_USER etc instead of hardcoding them.

def get_db():
    return pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="devuser",
        password="devpassword",
        database="devlab"
    )

def fetch_and_store(artist):
    print(f"Searching iTunes for: {artist}")

    #https://itunes.apple.com/search?term=Daft+Punk&media=music&limit=10


    response = requests.get(
        "https://itunes.apple.com/search",
        params={
            "term": artist,
            "media": "music",
            "limit": 10
        }
    )

    data = response.json()
    results = data.get("results", []) #Built-in Python module — no installation needed. Used to read environment variables with os.getenv(). In our script we use it to get the database connection details like DB_HOST, DB_PORT, DB_USER etc instead of hardcoding them.
    #.get() is a Python dictionary method that safely retrieves a value by key.
    if not results:
        print("No results found.")
        return

    conn = get_db()
    cursor = conn.cursor()

    for track in results:
        #From that line onwards you're parsing the dictionary.
        artist_name = track.get("artistName", "") # same as doing: artist_name = track["artistName"]
        track_name = track.get("trackName", "")
        album = track.get("collectionName", "")
        released = track.get("releaseDate", "")[:10] #slice the string to keep only date part "2000-11-30" instead of "2000-11-30T08:00:00Z"

        cursor.execute("""
            INSERT INTO songs (artist, track_name, album, released_date)
            VALUES (%s, %s, %s, %s)
        """, (artist_name, track_name, album, released))

        print(f"Stored: {track_name} — {album} ({released})")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nDone! {len(results)} songs stored in MariaDB.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_music.py <artist name>")
        sys.exit(1)

    artist = " ".join(sys.argv[1:])
    fetch_and_store(artist)