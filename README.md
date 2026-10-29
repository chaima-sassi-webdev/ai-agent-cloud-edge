# AI Agent for Autonomous Software Engineering in Cloud–Edge Environments

> **Academic Capstone Project** réalisé chez **Placeholder Tunisie** (Janvier 2025 - Juin 2025).  
> Système d'agent intelligent hybride conçu pour planifier, exécuter et auto-corriger des tâches d'ingénierie logicielle à travers des environnements Cloud centralisés et des nœuds Edge contraints.

---

## 🏗️ Architecture Globale (Cloud-Edge)

Le projet repose sur une séparation claire des responsabilités entre le Cloud et la périphérie (Edge) :
- **Noyau Cloud (Le Cerveau) :** Héberge le moteur de planification, gère l'interaction avec le LLM (OpenAI API) et supervise le cycle de vie global des tâches logicielles.
- **Nœuds Edge (La Zone d'Exécution) :** Reçoit les instructions et déploie le code généré dans des conteneurs **Docker** isolés et éphémères pour garantir la sécurité et la portabilité des tests.
- **Boucle de Rétroaction (Feedback Loop) :** Capture automatique des erreurs d'exécution (`stderr`) sur l'Edge pour les réinjecter dynamiquement au LLM dans le Cloud, permettant une auto-correction itérative.

---

## 📂 Structure du Projet

```text
ai-agent-cloud-edge/
│
├── docker/
│   └── Dockerfile          # Environnement d'exécution isolé (Edge/Python)
│
├── src/
│   ├── agent.py            # Logique de l'agent et intégration du LLM
│   └── main.py             # Orchestration et boucle d'auto-correction (Feedback Loop)
│
├── tests/                  # Cas de test et scénarios de validation E2E
│
└── README.md               # Documentation technique du projet
