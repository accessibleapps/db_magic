"""Ordered, transactional database schema upgrades."""

from logging import getLogger

logger = getLogger("db_magic.schema_upgrades")


def perform_upgrade(session, upgrades=None, schema_version=0):
    """Upgrade a database one committed schema version at a time."""
    if upgrades is None:
        upgrades = {}

    current_version = int(session.execute("PRAGMA user_version").scalar())
    logger.info(
        "Current schema version: %d, desired schema version: %d",
        current_version,
        schema_version,
    )
    if current_version >= schema_version:
        return

    for version in range(current_version + 1, schema_version + 1):
        logger.info("Applying schema version %d", version)
        try:
            version_upgrades = upgrades[version]
            connection = session.connection().connection
            connection.execute("BEGIN")
            for upgrade in version_upgrades:
                if callable(upgrade):
                    upgrade(session, connection)
                else:
                    connection.execute(upgrade)
            session.execute(f"PRAGMA user_version={version}")
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Failed upgrading to version %d", version)
            raise
        logger.info("Upgraded to schema version %d", version)
