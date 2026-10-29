from setuptools import setup, find_packages

__version__ = "1.0.0"

__doc__ = """SQLAlchemy model conventions and transactional SQLite upgrades"""

setup(
 name = "db_magic",
 version = __version__,
 description = __doc__,
 packages = find_packages(),
 package_data = {"db_magic": ["py.typed"]},
 python_requires = ">=3.8",
 install_requires = [
  'sqlalchemy>=2.0,<2.1',
 ],
 classifiers = [
  'Development Status :: 3 - Alpha',
  'Intended Audience :: Developers',
  'Programming Language :: Python',
  'Topic :: Software Development :: Libraries',
 ],
)
