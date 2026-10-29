from datetime import datetime  # pour générer les horodatages automatiques
from sqlalchemy import Column, DateTime, Float, Integer, String, Text  # pour structurer les tables

from src.api.database import Base  # pour lier la classe Python à une table SQL


class TaskDB(Base):  # la table relationnelle de stockage des tâches
  __tablename__ = "tasks"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(String, index=True, default="default_user")
  prompt = Column(Text, nullable=False)
  status = Column(
      String, default="pending"
  )  # pending, success, failed: état d'exécution de la tâche
  output = Column(Text, nullable=True)
  created_at = Column(DateTime, default=datetime.utcnow)

  # --- NOUVELLES COLONNES DE MÉTRIQUES (PFE Observabilité) ---
  attempts_count = Column(
      Integer, default=1
  )  # Nombre d'essais (boucle d'auto-correction)
  llm_latency_sec = Column(
      Float, nullable=True
  )  # Temps de génération de l'IA (Cloud)
  edge_latency_sec = Column(
      Float, nullable=True
  )  # Temps d'exécution dans le Sandbox (Edge)
  total_duration_sec = Column(
      Float, nullable=True
  )  # Durée totale de bout en bout
