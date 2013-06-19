import hackt
from database.database import init_db

app = hackt.create_app()
init_db()