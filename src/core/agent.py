import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from src.edge.sandbox import edge_sandbox

load_dotenv(override=True)
print("--> CLE RECUPEREE PAR PYTHON :", os.environ.get("GROQ_API_KEY"))


class AgentCore:
  """Client LLM principal"""

  def __init__(self):
    self.client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"), 
        base_url="https://api.groq.com/openai/v1"
    )

  def generate_solution(self, prompt: str) -> str:
    response = self.client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content


# Instance unique partagée
agent_core = AgentCore()


class CloudGeneratorAgent:
  """Agent 1 : Responsable de la génération initiale du code à partir du prompt."""

  def generate(self, prompt: str) -> tuple[str, float]:
    t0 = time.time()
    code = agent_core.generate_solution(prompt)
    latency = time.time() - t0
    return code, latency


class CloudAuditorAgent:
  """Agent 3 : Analyse les échecs d'exécution et génère un diagnostic correctif."""

  def audit_and_correct(self, failed_code: str, error_message: str) -> str:
    correction_prompt = (
        f"Le code Python suivant a produit une erreur dans le sandbox Edge :\n"
        f"```python\n{failed_code}\n```\n"
        f"Erreur capturée :\n```\n{error_message}\n```\n"
        f"Analyse l'erreur et fournis une version corrigée du code complet."
    )
    return agent_core.generate_solution(correction_prompt)


class EdgeExecutionAgent:
  """Agent 2 : Exécute et supervise le code dans l'environnement isolé Edge (Docker)."""

  def execute(self, code: str) -> tuple[dict, float]:
    t0 = time.time()
    result = edge_sandbox.execute_code(code)
    latency = time.time() - t0
    return result, latency
