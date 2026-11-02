import base64
import hashlib
import re
import sqlite3
from contextlib import closing


def evaluate(data, database=":memory:"):
    digest, count = data["sha256"], data["count"]
    if not re.fullmatch("[0-9a-f]{64}", digest) or type(count) is not int or not 1 <= count <= 4096:
        raise ValueError("invalid manifest")
    with closing(sqlite3.connect(database)) as db:
        db.executescript("""CREATE TABLE IF NOT EXISTS files(hash TEXT PRIMARY KEY, count INTEGER);
                            CREATE TABLE IF NOT EXISTS parts(hash TEXT, i INTEGER, bytes BLOB, PRIMARY KEY(hash,i));""")
        with db:
            db.execute("INSERT OR IGNORE INTO files VALUES(?,?)", (digest,count))
            if db.execute("SELECT count FROM files WHERE hash=?",(digest,)).fetchone()[0] != count:
                raise ValueError("manifest conflict")
            for chunk in data["chunks"]:
                index = chunk["index"]
                if type(index) is not int or not 0 <= index < count:
                    raise ValueError("invalid chunk index")
                payload = base64.b64decode(chunk["base64"],validate=True)
                if len(payload)>1048576:
                    raise ValueError("chunk exceeds limit")
                db.execute("INSERT OR IGNORE INTO parts VALUES(?,?,?)",(digest,index,payload))
                if db.execute("SELECT bytes FROM parts WHERE hash=? AND i=?",(digest,index)).fetchone()[0] != payload:
                    raise ValueError("chunk conflict")
            parts = dict(db.execute("SELECT i,bytes FROM parts WHERE hash=?",(digest,)))
            missing = sorted(set(range(count))-parts.keys())
            if missing:
                return {"state":"pending","missing":missing}
            full = b"".join(parts[i] for i in range(count))
            if hashlib.sha256(full).hexdigest() != digest:
                raise ValueError("assembled digest mismatch")
            return {"state":"verified","base64":base64.b64encode(full).decode("ascii")}
