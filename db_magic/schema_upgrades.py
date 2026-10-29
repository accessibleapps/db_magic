"""Ordered, transactional database schema upgrades."""

from logging import getLogger
from typing import Callable, Mapping, Optional, Sequence, Union

from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

logger = getLogger("db_magic.schema_upgrades")


Upgrade = Union[str, Callable[[Session, Connection], None]]


def perform_upgrade(
    session: Session,
    upgrades: Optional[Mapping[int, Sequence[Upgrade]]] = None,
    schema_version: int = 0,
) -> None:
    """Upgrade SQLite one transaction per version, including its version marker.

    Callbacks receive the session and its SQLAlchemy connection. They must leave
    commit and rollback to this runner. Run before starting application work.
    """
    if upgrades is None:
        upgrades = {}

    connection = session.connection()
    current_version = int(connection.exec_driver_sql("PRAGMA user_version").scalar_one())
    logger.info(
        "Current schema version: %d, desired schema version: %d",
        current_version,
        schema_version,
    )
    if current_version > schema_version:
        raise ValueError(
            f"Database schema version {current_version} is newer than supported "
            f"version {schema_version}"
        )
    if current_version == schema_version:
        return

    missing = [version for version in range(current_version + 1, schema_version + 1)
               if version not in upgrades]
    if missing:
        raise ValueError(f"Missing schema upgrades: {missing}")

    for version in range(current_version + 1, schema_version + 1):
        logger.info("Applying schema version %d", version)
        try:
            version_upgrades = upgrades[version]
            connection = session.connection()
            # sqlite3's legacy transaction mode does not begin for DDL. Explicit
            # BEGIN keeps ALTER TABLE and user_version in the same transaction.
            connection.exec_driver_sql("BEGIN")
            for upgrade in version_upgrades:
                if callable(upgrade):
                    upgrade(session, connection)
                else:
                    connection.exec_driver_sql(upgrade)
            connection.exec_driver_sql(f"PRAGMA user_version={version}")
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed upgrading to version %d", version)
            raise
        logger.info("Upgraded to schema version %d", version)
