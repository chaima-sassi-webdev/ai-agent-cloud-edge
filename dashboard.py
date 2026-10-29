import requests
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Cloud-Edge Multi-Agent Dashboard", page_icon="🤖", layout="wide"
)

st.title("🌐 Cloud-Edge Multi-Agent System Dashboard")
st.markdown(
    "Interface de pilotage et d'évaluation du système multi-agents à boucle"
    " fermée (*Cloud ⇄ Edge*)."
)

# Sidebar pour la configuration
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input(
    "URL de l'API FastAPI", value="http://localhost:8000/run-task"
)
user_id = st.sidebar.number_input("User ID", value=1, step=1)

# Zone principale : Prompt utilisateur
st.subheader("📝 Soumettre une tâche au pipeline multi-agents")
prompt = st.text_area(
    "Entrez votre instruction ou code à générer/exécuter :",
    placeholder=(
        "Ex: Écris un script Python qui calcule la suite de Fibonacci et gère"
        " les erreurs potentielles."
    ),
    height=120,
)

if st.button("🚀 Lancer le pipeline", type="primary", use_container_width=True):
  if not prompt.strip():
    st.warning("Veuillez entrer un prompt valide.")
  else:
    with st.spinner(
        "Exécution en cours de la boucle Cloud (Générateur/Auditeur) ⇄ Edge"
        " (Sandbox Docker)..."
    ):
      try:
        payload = {"user_id": str(user_id), "user_prompt": prompt}
        response = requests.post(api_url, json=payload, timeout=60)

        if response.status_code == 200:
          data = response.json()
          status = data.get("status")
          metrics = data.get("metrics", {})

          # Affichage du statut global
          if status == "success":
            st.success(
                f"✅ Tâche réussie et convergée en **{metrics.get('attempts', 1)}**"
                " tentative(s) !"
            )
          else:
            st.error(
                "❌ Échec de la tâche après épuisement des tentatives"
                " d'auto-guérision."
            )

          # Métriques clés sous forme de colonnes (très utile pour le rapport de PFE)
          col1, col2, col3, col4 = st.columns(4)
          col1.metric(
              "Tentatives (Itérations)",
              metrics.get("attempts", "-"),
              help="Nombre de boucles Generator ➔ Edge ➔ Auditor",
          )
          col2.metric(
              "Latence LLM (Cloud)",
              f"{metrics.get('llm_latency_seconds', 0)}s",
          )
          col3.metric(
              "Latence Edge (Docker)",
              f"{metrics.get('edge_latency_seconds', 0)}s",
          )
          col4.metric(
              "Durée Totale", f"{metrics.get('total_duration_seconds', 0)}s"
          )

          # Résultats détaillés par onglets
          tab1, tab2 = st.tabs(
              [
                  "💻 Code Final Généré / Corrigé (Cloud)",
                  "⚙️ Rapport d'Exécution Sandbox (Edge)",
              ]
          )

          with tab1:
            st.code(data.get("cloud_output", ""), language="python")

          with tab2:
            edge_res = data.get("edge_execution", {})
            st.json(edge_res)

        else:
          st.error(f"Erreur serveur ({response.status_code}): {response.text}")

      except requests.exceptions.ConnectionError:
        st.error(
            "Impossible de se connecter à l'API. Vérifiez que votre serveur"
            " Uvicorn est bien démarré sur `http://localhost:8000`."
        )
      except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
