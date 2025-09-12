# -*- coding: utf-8 -*-
"""
Script para probar el agente localmente.

Uso:
  - Prueba sin AWS (modo mock):
      python -m src.run_agent --text "¿Cuál es mi saldo?" --mock

  - Prueba con AWS real (necesitas credenciales/variables de entorno):
      export AWS_REGION=us-east-1
      export CRM_URL=http://localhost:8000/api
      python -m src.run_agent --text "Quiero hacer una transferencia"

Opciones principales:
  --text: texto del usuario (requerido)
  --mock: usa clientes mock (no hace llamadas a AWS ni al CRM)
  --lex-bot-id / --lex-bot-alias-id / --lex-locale-id: para pasar ids de Lex si los tienes
  --bedrock-model-id: para pasar model_id de Bedrock si lo usas

El script imprime el resultado devuelto por Agent.handle_message.

"""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from src.agent import Agent
from src import aws_clients


class MockLexClient:
    def recognize_text(self, **kwargs):
        # Respuesta simulada sencilla
        text = kwargs.get("text", "")
        if "saldo" in text or "saldo" in text.lower():
            return {
                "sessionState": {"intent": {"name": "ConsultarSaldo"}},
                "messages": [{"contentType": "PlainText", "content": "Tu saldo es S/ 1,234.56"}],
            }
        return {"sessionState": {"intent": {}}, "messages": []}


class MockBedrockClient:
    def invoke_model(self, modelId=None, body=None, contentType=None, accept=None, **kwargs):
        # Lee prompt y devuelve una estructura similar a la esperada en src/agent
        try:
            payload = json.loads(body)
            prompt = payload.get("prompt") or payload.get("inputText") or ""
        except Exception:
            prompt = str(body)
        fake = {"body": FakeBody({"completion": f"(mock) Respuesta generada para: {prompt}"})}
        return fake


class FakeBody:
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def read(self):
        return json.dumps(self._data).encode("utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text", required=True, help="Texto del usuario a procesar")
    p.add_argument("--mock", action="store_true", help="Usar clientes mock (sin llamadas AWS)")
    p.add_argument("--lex-bot-id", help="Lex botId si lo usas")
    p.add_argument("--lex-bot-alias-id", help="Lex botAliasId si lo usas")
    p.add_argument("--lex-locale-id", default="es_419", help="Lex localeId")
    p.add_argument("--bedrock-model-id", help="Bedrock model id si lo usas")
    args = p.parse_args()

    if args.mock:
        lex_client = MockLexClient()
        bedrock_client = MockBedrockClient()
        agent = Agent(lex_client=lex_client, bedrock_client=bedrock_client)
    else:
        # usa los clientes reales (requiere boto3 configurado)
        lex_client = aws_clients.get_lex_client()
        bedrock_client = aws_clients.get_bedrock_client()
        agent = Agent(lex_client=lex_client, bedrock_client=bedrock_client)

    event = {
        "text": args.text,
        "lex_bot_id": args.lex_bot_id,
        "lex_bot_alias_id": args.lex_bot_alias_id,
        "lex_locale_id": args.lex_locale_id,
        "bedrock_model_id": args.bedrock_model_id,
    }

    result = agent.handle_message(event)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
