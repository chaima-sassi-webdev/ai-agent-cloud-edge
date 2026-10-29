import os
from sqlalchemy import create_engine  #pour créer le moteur de connexion physique à la base de données
from sqlalchemy.ext.declarative import declarative_base  # définir les modèles ORM
from sqlalchemy.orm import sessionmaker # gérer les sessions de requêtes SQL

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/ai_agent_db" #définir l'URL de conx à PostgreSQL
)

engine = create_engine(SQLALCHEMY_DATABASE_URL) #crée le moteur SQLAlchemy pour gèrer les conx avec PostgreSQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #désactive l'auto-commit; l'auto-flush pour un contrôle précis.

Base = declarative_base() #crée la classe de base pour l'héritage de tous les modèles de tables de la base de données. 

def get_db():  #déclare la fonction utilitaire d'injection de dépendances pour FastAPI
    db = SessionLocal() #instancie une nouvelle conx de bd 
    try: 
        yield db #fournit la session active à la route FastAPI
    finally:  #bloc exécuté à la fin de la requête, qu'elle réussisse ou qu'elle plante.
        db.close() #ferme la session pour libérer la ressource et éviter les fuites de conx.
