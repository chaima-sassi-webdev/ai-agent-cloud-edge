import time
from src.core.agent import (
    CloudAuditorAgent,
    CloudGeneratorAgent,
    EdgeExecutionAgent,
)


class MultiAgentOrchestrator:

  def __init__(self, max_retries: int = 3):
    self.generator = CloudGeneratorAgent()
    self.auditor = CloudAuditorAgent()
    self.edge_agent = EdgeExecutionAgent()
    self.max_retries = max_retries

  def run_pipeline(self, initial_prompt: str) -> dict:
    attempts = 0
    llm_total_latency = 0.0
    edge_total_latency = 0.0

    current_prompt = initial_prompt
    current_code = ""
    execution_result = {}

    while attempts < self.max_retries:
      attempts += 1

      if attempts == 1:
        current_code, llm_lat = self.generator.generate(current_prompt)
      else:
        error_msg = execution_result.get("output", "Erreur inconnue")
        t0 = time.time()
        current_code = self.auditor.audit_and_correct(current_code, error_msg)
        llm_lat = time.time() - t0

      llm_total_latency += llm_lat

      execution_result, edge_lat = self.edge_agent.execute(current_code)
      edge_total_latency += edge_lat

      if execution_result.get("exit_code") == 0:
        return {
            "status": "success",
            "attempts": attempts,
            "cloud_output": current_code,
            "edge_execution": execution_result,
            "llm_latency": round(llm_total_latency, 3),
            "edge_latency": round(edge_total_latency, 3),
        }

    return {
        "status": "failed",
        "attempts": attempts,
        "cloud_output": current_code,
        "edge_execution": execution_result,
        "llm_latency": round(llm_total_latency, 3),
        "edge_latency": round(edge_total_latency, 3),
    }
