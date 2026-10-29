import os

class AIAgent:
    def __init__(self, api_key: str = None):
        pass

    def generate_code(self, prompt: str) -> str:
        if "corrige" in prompt.lower() or "échoué" in prompt.lower():
            return "total = sum(range(1, 11))\nprint('Somme corrigée : ' + str(total))"
        else:
            return "total = sum(range(1, 11))\nprint(variable_inexistante)"
