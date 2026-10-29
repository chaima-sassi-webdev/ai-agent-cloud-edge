import ast       #pour analyser la structure syntaxique du code Python avant exécution
import docker    #pour piloter le démon Docker et lancer des conteneurs 
from pathlib import Path   #pour manipuler les fichiers et les dossiers 

BASE_WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"  #définit le chemin du dossier "workspace" 

class EdgeSandbox:                        #responsable de l'exécution isolée et sécurisée du code 
    def __init__(self):
        self.client = docker.from_env()   #initialisation de client Docker en se connectant au socket de l'hôte

    def execute_code(self, python_code: str, user_id: str = "default_user") -> dict:    #Méthode qui reçoit le code et l'ID utilisateur
        """
        Exécute du code Python dans un conteneur Docker Sandbox hautement sécurisé et isolé.
        Applique une validation AST, des quotas stricts, un timeout et un volume par utilisateur.
        """
        
        try:
            ast.parse(python_code)        #vérification le syntaxe de code Python sans exécution 
        except SyntaxError as e:          #intercepte une erreur de syntaxe si le code est mal formé
            return {
                "exit_code": 1,
                "output": f"Erreur de syntaxe détectée avant exécution (AST) : {str(e)}"
            }
        user_workspace = BASE_WORKSPACE / user_id         #Crée un chemin de dossier pour l'utilisateur courant
        user_workspace.mkdir(parents=True, exist_ok=True) #Crée automatiquement le dossier utilisateur et ses parents s'il n'existent pas 
        
        script_path = user_workspace / "script.py"             #Définit le chemin de fichier de script à exécuter 
        script_path.write_text(python_code, encoding="utf-8")  #Ecrit le code généré par l'IA dans le fichier script.py en UTF-8

        container = None      #pour la gestion du cycle de vie
        try:
           
            container = self.client.containers.create(    #création du conteneur sans le démarrer avec des contraintes strictes 
                image="python:3.10-slim",                 
                command=["python", "/app/script.py"],     #Commande à utiliser lors de démarrage de conteneur
                volumes={                    #Configurer les volumes partagés entre l'hôte et le conteneur
                    str(user_workspace): {
                        "bind": "/app",
                        "mode": "rw"  # Accès en lecture/écriture restreint à l'espace de l'utilisateur
                    }
                },
                working_dir="/app",
                network_mode="none",
                mem_limit="256m",
                cpu_period=100000,
                cpu_quota=50000,  # Limitation stricte du CPU
                detach=True
            )
            
            container.start()    #Démarrer le conteneur Docker créé.
            
            # 4. Attente de l'exécution avec un Timeout strict de 5 secondes
            result = container.wait(timeout=5)
            exit_code = result.get("StatusCode", 1)   #récupère le code de sortie du script (0 = succès)
            
            # Récupération des logs d'exécution (stdout / stderr)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            
            return {                       #retourne le résultat complet de l'exécution
                "exit_code": exit_code,
                "output": logs
            }

        except Exception as e:
            return {
                "exit_code": 1,
                "output": f"Erreur d'exécution ou timeout dépassé (max 5s) : {str(e)}"
            }
        finally:
            # Nettoyage systématique du conteneur éphémère
            if container:
                try:
                    container.remove(force=True)   #pour libérer l'espace disque
                except:
                    pass

# Instance unique exportée pour être appelée dans l'API Gateway
edge_runner = EdgeSandbox()
