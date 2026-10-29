import os
import docker
from agent import AIAgent

def execute_code_in_edge(code: str):
    """Exécute le code généré dans un conteneur Docker isolé (Edge) et capture les erreurs."""
    client = docker.from_env()
    print("[*] Lancement de l'exécution dans le conteneur Edge...")
    
    try:
        container_output = client.containers.run(
            image="python:3.10-slim",
            command=["python", "-c", code],
            remove=True,
            stderr=True,
            stdout=True
        )
        return True, container_output.decode("utf-8")
    
    except docker.errors.ContainerError as e:
        error_msg = e.stderr.decode("utf-8") if e.stderr else str(e)
        return False, error_msg
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    agent = AIAgent()
    
    task_prompt = "Écris un script Python qui calcule la somme des nombres de 1 à 10 et affiche le résultat."
    
    print(f"[*] Objectif confié à l'agent : {task_prompt}\n")
    
    raw_code = agent.generate_code(task_prompt)
    clean_code = raw_code.replace("```python", "").replace("```", "").strip()
    
    print(f"--- Code Généré ---\n{clean_code}\n-------------------")
    
    success, output = execute_code_in_edge(clean_code)
    
    max_retries = 3
    attempt = 1
    
    while not success and attempt <= max_retries:
        print(f"\n[!] Échec détecté (Tentative {attempt}/{max_retries}). Envoi de l'erreur au LLM pour correction...")
        print(f"Détail de l'erreur :\n{output}")
        
        correction_prompt = (
            f"Le code Python suivant a échoué :\n{clean_code}\n\n"
            f"Voici l'erreur retournée :\n{output}\n\n"
            "Corrige le code pour résoudre cette erreur. Retourne uniquement le code Python valide."
        )
        
        raw_code = agent.generate_code(correction_prompt)
        clean_code = raw_code.replace("```python", "").replace("```", "").strip()
        
        print(f"\n--- Code Corrigé (Tentative {attempt}) ---\n{clean_code}\n------------------------------------------")
        
        success, output = execute_code_in_edge(clean_code)
        attempt += 1

    if success:
        print(f"\n[SUCCÈS] Le code s'est exécuté correctement :\n{output}")
    else:
        print(f"\n[ÉCHEC DÉFINITIF] L'agent n'a pas pu résoudre l'erreur après {max_retries} tentatives.")
