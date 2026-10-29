from openai import OpenAI  # Pour configurer le client de communication

client = OpenAI(   # Initialise le client API
    base_url="http://localhost:11434/v1",  #Redirige l'adresse vers le serveur local Ollama
    api_key="ollama"   #Fournit une clé factice (Ollama n'en a pas besoin, mais la bibliothèque l'exige) 
)

class AIAgentCore:   #Déclare la classe principale qui gère le comportement de l'IA
    def __init__(self, model_name: str = "llama3"):  # Constructeur exécuté à l'instanciation avec "llama3" par défaut
        self.model_name = model_name  #Enregistre le nom du modèle local à utiliser
        self.system_prompt = (   #Début du bloc texte définissant le rôle et les contraintes de l'agent
            "Vous êtes un agent logiciel autonome de niveau industriel intégré dans une plateforme Cloud-Edge. "
            "Votre rôle est d'analyser les requêtes des utilisateurs, de concevoir des solutions logicielles propres, "
            "et de générer du code Python robuste, sécurisé et prêt à être exécuté dans un environnement isolé (sandbox)."
        )

    def generate_solution(self, user_prompt: str) -> str:   #Méthode prenant le texte utilisateur et retournant du texte
        try:
            response = client.chat.completions.create(   #Envoie la requête de chat au serveur Ollama local 
                model=self.model_name,  #Précise quel modèle local doit répondre (ex: llama3) 
                messages=[  #Ouvre la liste des messages 
                    {"role": "system", "content": self.system_prompt},  #Transmet le rôle et les règles strictes de l'agent
                    {"role": "user", "content": user_prompt} #Transmet la question ou la tâche demandée par l'utilisateur
                ],
                temperature=0.2, #Réduit la créativité de l'IA pour privilégier la stabilité du code.
                max_tokens=1500 #Fixe une limite maximale sur la longueur de la réponse générée.
            )
            return response.choices[0].message.content   #Extrait et retourne uniquement le contenu textuel de la réponse.
        except Exception as e:  #Intercepte toute erreur survenue ( ollama éteint ou inaccessible) 
            raise RuntimeError(f"Erreur lors de la communication avec le LLM local : {str(e)}")

agent_core = AIAgentCore() #crée une instance unique (singleton) prête à être importée dans votre API FastAPI. 
