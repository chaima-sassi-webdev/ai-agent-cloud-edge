import re
import io
import tarfile
import docker


class EdgeSandbox:
    @staticmethod
    def clean_llm_code(raw_response: str) -> str:
        """Extrait proprement le code Python d'une réponse LLM,
        même si le modèle a ajouté du texte ou des explications autour.
        """
        if not raw_response:
            return "print('Erreur : Code vide')"

        matches = re.findall(r"```(?:python)?\s*(.*?)\s*```", raw_response, re.DOTALL)
        if matches:
            return max(matches, key=len)
        return raw_response

    def __init__(self, image_name: str = "python:3.11-slim"):
        self.image_name = image_name
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise RuntimeError(
                f"Impossible de se connecter au démon Docker : {str(e)}"
            )

    def execute_code(self, code: str, timeout_seconds: int = 10) -> dict:
        """Exécute du code Python dans un conteneur Docker éphémère,
        totalement isolé et sécurisé (Sandbox) via injection directe à la racine.
        """
        clean_code = self.clean_llm_code(code)

        if not clean_code.strip():
            return {
                "exit_code": -1,
                "output": "Erreur Sandbox : Aucun code Python valide n'a pu être extrait.",
            }

        container = None
        try:
            # 1. Création du conteneur ciblant /script.py à la racine
            container = self.client.containers.create(
                image=self.image_name,
                command=["python", "/script.py"],
                network_mode="none",
                mem_limit="256m",
                cpu_quota=50000,
                pids_limit=50,
                detach=True,
            )

            # 2. Création d'une archive tar en mémoire contenant script.py
            tar_buffer = io.BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                file_data = clean_code.encode("utf-8")
                tarinfo = tarfile.TarInfo(name="script.py")
                tarinfo.size = len(file_data)
                tar.addfile(tarinfo, io.BytesIO(file_data))
            tar_buffer.seek(0)

            # 3. Injection directe à la racine "/" (qui existe toujours)
            container.put_archive("/", tar_buffer.read())

            # 4. Lancement de l'exécution
            container.start()

            # 5. Attente et récupération des logs
            result = container.wait(timeout=timeout_seconds)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
            exit_code = result.get("StatusCode", -1)

            return {"exit_code": exit_code, "output": logs}

        except Exception as e:
            return {
                "exit_code": -1,
                "output": f"Erreur d'exécution dans le Sandbox Edge : {str(e)}",
            }

        finally:
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass


# Instance globale du sandbox Edge
edge_sandbox = EdgeSandbox()
