import time
import os
import sys

# --- AJOUT PROGRAMMATIQUE DE LA RACINE DU PROJET ---
# Permet à Python de trouver le dossier 'src' peu importe comment le serveur est lancé
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if root_dir not in sys.path:
  sys.path.insert(0, root_dir)


from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
# Assurez-vous d'avoir vos imports habituels (db, models, schemas, agent_core, edge_sandbox)
from src.core.orchestrator import MultiAgentOrchestrator
from src.core.agent import agent_core
from src.api.database import Base, engine, get_db
from src.api.models import TaskDB
from src.api.schemas import TaskRequest, TaskResponse  # <-- C'est ici qu'ils doivent être importés
from src.edge.sandbox import edge_sandbox

# 1. INITIALISATION DE L'APPLICATION (Doit être en premier)
app = FastAPI(
    title="AI Agent Cloud-Edge API",
    description=(
        "API Gateway pour agent autonome Cloud-Edge avec Sandbox Docker"
    ),
    version="1.0.0",
)
Base.metadata.create_all(
    bind=engine
)
@app.get("/", response_class=HTMLResponse)
async def home_ui():
  return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloud-Edge AI Agent - PFE Demo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-gray-100 font-sans min-h-screen flex flex-col items-center justify-center p-6">
        
        <div class="w-full max-w-3xl bg-gray-800 rounded-2xl shadow-2xl p-8 border border-gray-700">
            <div class="flex items-center space-x-3 mb-6">
                <span class="text-3xl">⚡</span>
                <div>
                    <h1 class="text-2xl font-bold">Cloud-Edge AI Agent</h1>
                    <p class="text-sm text-gray-400">Pipeline autonome : Génération LLM (Cloud) & Sandbox Docker (Edge)</p>
                </div>
            </div>

            <!-- Formulaire de prompt -->
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">Votre Prompt / Instruction :</label>
                    <textarea id="promptInput" rows="3" class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none" placeholder="Ex: Écris un script Python qui calcule la factorielle de 5..."></textarea>
                </div>
                <button onclick="runTask()" id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-lg transition duration-200 flex items-center justify-center space-x-2">
                    <span>Lancer l'Exécution du Pipeline</span>
                </button>
            </div>

            <!-- Indicateur de chargement -->
            <div id="loader" class="hidden mt-6 text-center text-indigo-400 animate-pulse">
                ⏳ Exécution en cours (Cloud LLM + Edge Docker Sandbox + Self-Healing)...
            </div>

            <!-- Résultats dynamiques -->
            <div id="results" class="hidden mt-8 space-y-6 border-t border-gray-700 pt-6">
                <h2 class="text-lg font-semibold text-indigo-400">Résultats de l'Exécution :</h2>
                
                <!-- Message & Statut -->
                <div id="statusMessage" class="p-3 rounded-lg text-sm font-medium"></div>

                <!-- Grille des étapes -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Cloud Output -->
                    <div class="bg-gray-900 p-4 rounded-xl border border-gray-700">
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">☁️ 1. Code Généré (Cloud / LLM)</h3>
                        <pre id="cloudOutput" class="text-xs text-green-400 bg-black p-3 rounded overflow-x-auto font-mono"></pre>
                    </div>

                    <!-- Edge Execution -->
                    <div class="bg-gray-900 p-4 rounded-xl border border-gray-700">
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">🛡️ 2. Sandbox (Edge / Docker)</h3>
                        <div class="text-xs space-y-1 mb-2 font-mono">
                            <div>Exit Code : <span id="exitCode" class="font-bold"></span></div>
                        </div>
                        <pre id="edgeOutput" class="text-xs text-blue-400 bg-black p-3 rounded overflow-x-auto font-mono"></pre>
                    </div>
                </div>

                <!-- Métriques -->
                <div class="bg-gray-900 p-4 rounded-xl border border-gray-700">
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">📊 3. Télémétrie & Métriques</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                        <div class="bg-black p-3 rounded">
                            <div class="text-xs text-gray-400">Tentatives</div>
                            <div id="metricAttempts" class="text-lg font-bold text-indigo-400"></div>
                        </div>
                        <div class="bg-black p-3 rounded">
                            <div class="text-xs text-gray-400">Latence LLM</div>
                            <div id="metricLlm" class="text-lg font-bold text-indigo-400"></div>
                        </div>
                        <div class="bg-black p-3 rounded">
                            <div class="text-xs text-gray-400">Latence Edge</div>
                            <div id="metricEdge" class="text-lg font-bold text-indigo-400"></div>
                        </div>
                        <div class="bg-black p-3 rounded">
                            <div class="text-xs text-gray-400">Durée Totale</div>
                            <div id="metricTotal" class="text-lg font-bold text-indigo-400"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function runTask() {
                const prompt = document.getElementById('promptInput').value;
                if (!prompt) return alert("Veuillez saisir un prompt !");

                const btn = document.getElementById('submitBtn');
                const loader = document.getElementById('loader');
                const results = document.getElementById('results');

                btn.disabled = true;
                loader.classList.remove('hidden');
                results.classList.add('hidden');

                try {
                    const response = await fetch('/run-task', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: 'pfe_web_demo', user_prompt: prompt })
                    });
                    const data = await response.json();

                    // Affichage des données
                    results.classList.remove('hidden');
                    
                    const statusDiv = document.getElementById('statusMessage');
                    if(data.status === 'success') {
                        statusDiv.className = "p-3 rounded-lg text-sm font-medium bg-green-900/50 text-green-300 border border-green-700";
                    } else {
                        statusDiv.className = "p-3 rounded-lg text-sm font-medium bg-red-900/50 text-red-300 border border-red-700";
                    }
                    statusDiv.innerText = data.message;

                    document.getElementById('cloudOutput').innerText = data.cloud_output || "Aucun code";
                    document.getElementById('exitCode').innerText = data.edge_execution.exit_code;
                    document.getElementById('exitCode').className = data.edge_execution.exit_code === 0 ? "text-green-400 font-bold" : "text-red-400 font-bold";
                    document.getElementById('edgeOutput').innerText = data.edge_execution.output || "Pas de sortie";

                    document.getElementById('metricAttempts').innerText = data.metrics.attempts;
                    document.getElementById('metricLlm').innerText = data.metrics.llm_latency_seconds + "s";
                    document.getElementById('metricEdge').innerText = data.metrics.edge_latency_seconds + "s";
                    document.getElementById('metricTotal').innerText = data.metrics.total_duration_seconds + "s";

                } catch (err) {
                    alert("Erreur de communication avec l'API FastAPI.");
                    console.error(err);
                } finally {
                    btn.disabled = false;
                    loader.classList.add('hidden');
                }
            }
        </script>
    </body>
    </html>
    """





@app.post("/run-task", response_model=TaskResponse)
def run_task(task: TaskRequest, db: Session = Depends(get_db)):
  start_total_time = time.time()
  db_task = None

  try:
    # 1. Enregistrement initial de la tâche en base de données
    db_task = TaskDB(
        user_id=task.user_id, prompt=task.user_prompt, status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 2. Utilisation de l'orchestrateur multi-agents (Cloud Generator + Edge Sandbox + Auditor)
    orchestrator = MultiAgentOrchestrator(max_retries=3)
    pipeline_result = orchestrator.run_pipeline(task.user_prompt)

    total_duration = time.time() - start_total_time

    # 3. Mise à jour des résultats finaux en base de données
    db_task.status = pipeline_result["status"]
    db_task.output = pipeline_result["cloud_output"]
    db_task.attempts_count = pipeline_result["attempts"]
    db_task.llm_latency_sec = pipeline_result["llm_latency"]
    db_task.edge_latency_sec = pipeline_result["edge_latency"]
    db_task.total_duration_sec = round(total_duration, 3)
    db.commit()
    db.refresh(db_task)

    metrics_data = {
        "attempts": db_task.attempts_count,
        "llm_latency_seconds": db_task.llm_latency_sec,
        "edge_latency_seconds": db_task.edge_latency_sec,
        "total_duration_seconds": db_task.total_duration_sec,
    }

    return TaskResponse(
        task_id=db_task.id,
        status=db_task.status,
        message=(
            f"Pipeline multi-agents exécuté en {db_task.attempts_count}"
            f" tentative(s) ({total_duration:.2f}s)"
        ),
        cloud_output=pipeline_result["cloud_output"],
        edge_execution=pipeline_result["edge_execution"],
        metrics=metrics_data,
    )

  except Exception as e:
    if db_task:
      db_task.status = "failed"
      db_task.output = str(e)
      db.commit()
    raise HTTPException(status_code=500, detail=str(e))
