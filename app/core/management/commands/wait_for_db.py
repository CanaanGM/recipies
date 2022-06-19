"""
django command to wait for ms.db to wake up
"""

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError

import time


class Command(BaseCommand):
    """django command to wait 4 db"""

    def handle(self, *ar, **kw):
        self.stdout.write("Waiting for DB . . .")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("DB unavailable, waiting for 1 second . . . ")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("DB available~!"))
