"""Executable schema-upgrade contracts."""

import sqlite3
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

    column_result = session.execute("PRAGMA table_info(example)")
    assert column_result is not None
    columns = {row[1] for row in column_result.fetchall()}
    assert columns == {"id", "title", "etag"}
    version_result = session.execute("PRAGMA user_version")
    assert version_result is not None
    assert version_result.scalar() == 3


def test_perform_upgrade_rolls_back_failed_version(tmp_path: Path) -> None:
    session = database_session(tmp_path / "rollback.db")

    with pytest.raises(sqlite3.OperationalError):
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

    column_result = session.execute("PRAGMA table_info(example)")
    assert column_result is not None
    columns = {row[1] for row in column_result.fetchall()}
    assert columns == {"id"}
    version_result = session.execute("PRAGMA user_version")
    assert version_result is not None
    assert version_result.scalar() == 1
