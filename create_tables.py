from backend.database import engine, Base
from backend.models import License

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")
