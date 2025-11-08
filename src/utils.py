import functools, sqlite3, hashlib, json, os
from pathlib import Path

DB_PATH = Path(__file__).parents[2] / "data" / "cache.db"
DB_PATH.parent.mkdir(exist_ok=True)

def _conn():
    return sqlite3.connect(DB_PATH, timeout=10)

def cache(key_prefix: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_str = json.dumps([args, kwargs], sort_keys=True, default=str)
            key = f"{key_prefix}_{hashlib.md5(arg_str.encode()).hexdigest()}"
            conn = _conn()
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, ts REAL)")
            cur.execute("SELECT value FROM cache WHERE key=?", (key,))
            row = cur.fetchone()
            if row:
                conn.close()
                return json.loads(row[0])
            result = func(*args, **kwargs)
            cur.execute("INSERT OR REPLACE INTO cache VALUES (?, ?, strftime('%s','now'))", (key, json.dumps(result)))
            conn.commit()
            conn.close()
            return result
        return wrapper
    return decorator
