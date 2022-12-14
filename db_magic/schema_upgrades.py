from logging import getLogger
logger = getLogger('db_magic.schema_upgrades')

def perform_upgrade(session, upgrades=None, schema_version=0):
 if upgrades is None:
  upgrades = {}
 connection = session.bind.raw_connection()
 current_version = int(connection.execute("pragma user_version").fetchone()[0])
 logger.info("Current schema version: %d, desired schema version: %d" % (current_version, schema_version))
 if current_version >= schema_version:
  return
 for version in xrange(current_version + 1, schema_version + 1):
  session.begin(subtransactions=True)
  logger.info("Applying schema version %d" % version)
  try:
   for item in upgrades[version]:
    if callable(item):
     item(session, connection)
    else:
     connection.execute(item)
  except:
   logger.exception("failed upgrading to version %d" % version)
   raise
   break
   session.commit()
  session.execute('pragma user_version=%d' % version)
  session.commit()
  logger.info("upgraded to schema version %d" % version)
 else:
  logger.warning("No upgrades available to fulfill upgrade request")
