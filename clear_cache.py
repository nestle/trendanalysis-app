import sqlite3

def clear_cache():
    """
    Connect to a SQLite database named 'cache.db' and clear the cache by deleting
    all entries from the 'cache' table.
    @return None
    """
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cache')
    conn.commit()
    conn.close()
    print("Cache cleared.")

if __name__ == "__main__":
    clear_cache()
