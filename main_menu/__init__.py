from django.conf import settings
from django.db.backends.signals import connection_created
import django.db.backends.sqlite3.base
def activate_WAL(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode = WAL;')
        cursor.execute('PRAGMA synchronous = normal;')
        cursor.execute('PRAGMA journal_size_limit = 6144000;')

connection_created.connect(activate_WAL)