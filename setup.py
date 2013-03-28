from setuptools import setup, find_packages

__version__ = 0.2

__doc__ = """Magic! A thin wrapper over SQLAlchemy to make it a bit more friendly"""

setup(
 name = "db_magic",
 version = __version__,
 description = __doc__,
 packages = find_packages(),
 install_requires = [
  'sqlalchemy',
 ],
 classifiers = [
  'Development Status :: 3 - Alpha',
  'Intended Audience :: Developers',
  'Programming Language :: Python',
  'Topic :: Software Development :: Libraries',
 ],
)
