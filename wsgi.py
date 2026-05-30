import psycogreen.gevent
psycogreen.gevent.patch_psycopg()

from app import create_app

app = create_app()
