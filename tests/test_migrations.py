import os
import sqlite3
import subprocess
import sys


def test_upgrade_and_downgrade(tmp_path):
    database = tmp_path / "migrations.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{database}"}

    def alembic(*args):
        subprocess.run(
            [sys.executable, "-m", "alembic", *args],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    alembic("upgrade", "head")
    alembic("check")
    with sqlite3.connect(database) as conn:
        assert conn.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "0001"
        conn.execute("INSERT INTO users VALUES ('1', 'Ana', 'ana@example.com', 20)")
        try:
            conn.execute("INSERT INTO users VALUES ('2', 'Ana', 'ana@example.com', 20)")
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("O banco deve impedir emails duplicados")
    alembic("downgrade", "base")
    with sqlite3.connect(database) as conn:
        assert not conn.execute("SELECT name FROM sqlite_master WHERE name='users'").fetchall()
