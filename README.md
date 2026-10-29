# db_magic

Small shared conventions for Accessible Apps models and SQLite upgrades, using
SQLAlchemy 2.0 on Python 3.8 or newer.

`Entity` is a native SQLAlchemy declarative base with an integer `id` and the
original CamelCase-to-table-name convention. `TableNameMixin` supplies just that
naming convention for applications with their own declarative base or primary
key. Models declare columns and relationships with SQLAlchemy's `Mapped`,
`mapped_column`, `ForeignKey`, and `relationship` APIs directly.

Applications own their engines, session factories, transactions, and session
cleanup. There are no model-attached sessions, query helpers, deferred
relationships, or SQLAlchemy re-exports.

`db_magic.schema_upgrades.perform_upgrade(session, upgrades, schema_version)`
reads SQLite's `user_version`, checks that every required upgrade exists, then
commits each version separately. A failed version rolls back its SQL and version
marker; previously completed versions remain committed. A database newer than
the requested version is rejected. Call this at startup before application work.
Upgrade entries are SQL strings or callbacks receiving a native SQLAlchemy
`Session` and `Connection`. Callbacks must not commit or roll back. Use
`connection.exec_driver_sql()` for driver SQL or `session.execute(text(...))`
for textual SQL through the session.

## Migrating from 0.2

Replace column and relationship macros with SQLAlchemy declarations, preserving
existing table names, column names, nullability, defaults, indexes, and foreign
keys. Import SQLAlchemy objects from SQLAlchemy. Replace model-attached sessions
and `query()` with the application's native session. Remove commits from upgrade
callbacks; the runner owns the transaction. Update consumer manifests and locks
together. Version 1.0 intentionally removes the old convenience API.

## Origin

The original mapping layer was adapted in January 2013 from Mike Bayer's May 17,
2011 post, [Magic, a "New" ORM](https://techspot.zzzeek.org/2011/05/17/magic-a-new-orm/).
The SQLite upgrade runner was extracted from QCast in March 2013. The original
repository did not include a license file; this change does not assign a license
to that historical material.
