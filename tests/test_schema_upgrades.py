"""Executable schema-upgrade contracts."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from db_magic.schema_upgrades import perform_upgrade


def database_session(path: Path) -> Session:
    engine = create_engine(f"sqlite:///{path}")
    session_type = sessionmaker(bind=engine)
    session = session_type()
    session.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")
    session.execute("PRAGMA user_version=1")
    session.commit()
    return session


def test_perform_upgrade_applies_each_version_on_python_3(tmp_path: Path) -> None:
    session = database_session(tmp_path / "upgrade.db")

    perform_upgrade(
        session,
        upgrades={
            2: ["ALTER TABLE example ADD COLUMN title VARCHAR"],
            3: ["ALTER TABLE example ADD COLUMN etag VARCHAR"],
        },
        schema_version=3,
    )

    columns = {
        row[1] for row in session.execute("PRAGMA table_info(example)").fetchall()
    }
    assert columns == {"id", "title", "etag"}
    assert session.execute("PRAGMA user_version").scalar() == 3


def test_perform_upgrade_rolls_back_failed_version(tmp_path: Path) -> None:
    session = database_session(tmp_path / "rollback.db")

    with pytest.raises(Exception):
        perform_upgrade(
            session,
            upgrades={
                2: [
                    "ALTER TABLE example ADD COLUMN title VARCHAR",
                    "THIS IS NOT SQL",
                ],
            },
            schema_version=2,
        )

    columns = {
        row[1] for row in session.execute("PRAGMA table_info(example)").fetchall()
    }
    assert columns == {"id"}
    assert session.execute("PRAGMA user_version").scalar() == 1
