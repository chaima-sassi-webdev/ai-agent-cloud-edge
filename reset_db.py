from src.api.database import engine, Base
from src.api.models import TaskDB  # Importe vos modèles pour que SQLAlchemy les connaisse

print("Suppression et recréation des tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Base de données réinitialisée avec succès !")
