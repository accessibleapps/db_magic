"""Executable schema-upgrade contracts."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from db_magic.schema_upgrades import perform_upgrade


def database_session(path: Path) -> Session:
    engine = create_engine(f"sqlite:///{path}")
    session_type = sessionmaker(bind=engine)
    session = session_type()
    session.execute(text("CREATE TABLE example (id INTEGER PRIMARY KEY)"))
    session.execute(text("PRAGMA user_version=1"))
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

    column_result = session.execute(text("PRAGMA table_info(example)"))
    assert column_result is not None
    columns = {row[1] for row in column_result.fetchall()}
    assert columns == {"id", "title", "etag"}
    version_result = session.execute(text("PRAGMA user_version"))
    assert version_result is not None
    assert version_result.scalar() == 3


def test_perform_upgrade_rolls_back_failed_version(tmp_path: Path) -> None:
    session = database_session(tmp_path / "rollback.db")

    with pytest.raises(OperationalError):
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

    column_result = session.execute(text("PRAGMA table_info(example)"))
    assert column_result is not None
    columns = {row[1] for row in column_result.fetchall()}
    assert columns == {"id"}
    version_result = session.execute(text("PRAGMA user_version"))
    assert version_result is not None
    assert version_result.scalar() == 1


def test_callback_and_marker_roll_back_together(tmp_path: Path) -> None:
    session = database_session(tmp_path / "callback.db")

    def change_schema(session, connection):
        connection.exec_driver_sql("ALTER TABLE example ADD COLUMN title VARCHAR")

    with pytest.raises(OperationalError):
        perform_upgrade(session, {2: [change_schema, "INVALID SQL"]}, 2)

    assert session.execute(text("PRAGMA user_version")).scalar_one() == 1
    assert [row[1] for row in session.execute(text("PRAGMA table_info(example)"))] == ["id"]


def test_completed_version_survives_later_failure(tmp_path: Path) -> None:
    session = database_session(tmp_path / "partial.db")
    with pytest.raises(OperationalError):
        perform_upgrade(session, {2: ["ALTER TABLE example ADD COLUMN title VARCHAR"],
                                  3: ["INVALID SQL"]}, 3)
    assert session.execute(text("PRAGMA user_version")).scalar_one() == 2
    assert [row[1] for row in session.execute(text("PRAGMA table_info(example)"))] == ["id", "title"]


def test_missing_upgrade_is_rejected_before_changes(tmp_path: Path) -> None:
    session = database_session(tmp_path / "missing.db")
    with pytest.raises(ValueError, match="Missing schema upgrades"):
        perform_upgrade(session, {2: ["ALTER TABLE example ADD COLUMN title VARCHAR"]}, 3)
    assert session.execute(text("PRAGMA user_version")).scalar_one() == 1
    assert [row[1] for row in session.execute(text("PRAGMA table_info(example)"))] == ["id"]


def test_newer_database_is_rejected(tmp_path: Path) -> None:
    session = database_session(tmp_path / "newer.db")
    with pytest.raises(ValueError, match="newer than supported"):
        perform_upgrade(session, schema_version=0)
