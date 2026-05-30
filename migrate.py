import sys
sys.path.insert(0, '/opt/nosignal')
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    try:
        db.session.execute(db.text('ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE'))
        db.session.commit()
        print('Added is_read column')
    except Exception as e:
        print('is_read:', str(e))
