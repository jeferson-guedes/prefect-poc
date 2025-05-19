#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para gatilho manual de fluxos no Apache Airflow
Útil para iniciar processamentos sob demanda
"""

import argparse
import requests
import json
import os
from datetime import datetime

# Configuração básica
AIRFLOW_API_BASE_URL = "http://localhost:8080/api/v1"
DEFAULT_USERNAME = "airflow"
DEFAULT_PASSWORD = "airflow"


def get_auth_header(username, password):
    """Retorna o cabeçalho de autenticação para a API do Airflow."""
    import base64
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    return {"Authorization": f"Basic {auth_b64}"}


def trigger_dag(dag_id, conf=None, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
    """
    Aciona um DAG específico via API REST do Airflow.
    
    Args:
        dag_id (str): ID do DAG a ser acionado
        conf (dict, opcional): Configuração a ser passada para o DAG
        username (str): Nome de usuário para autenticação
        password (str): Senha para autenticação
    
    Returns:
        dict: Resposta da API do Airflow
    """
    endpoint = f"{AIRFLOW_API_BASE_URL}/dags/{dag_id}/dagRuns"
    headers = get_auth_header(username, password)
    headers["Content-Type"] = "application/json"
    
    payload = {
        "dag_run_id": f"manual_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    }
    
    if conf:
        payload["conf"] = conf
    
    response = requests.post(
        endpoint,
        headers=headers,
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        print(f"DAG '{dag_id}' acionado com sucesso!")
        return response.json()
    else:
        print(f"Erro ao acionar DAG '{dag_id}': {response.status_code}")
        print(response.text)
        return None


def list_dags(username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
    """Lista todos os DAGs disponíveis."""
    endpoint = f"{AIRFLOW_API_BASE_URL}/dags"
    headers = get_auth_header(username, password)
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        dags = response.json()["dags"]
        print(f"DAGs disponíveis ({len(dags)}):")
        for dag in dags:
            active = "✓" if dag["is_active"] else "✗"
            paused = "pausado" if dag["is_paused"] else "ativo"
            print(f"- {dag['dag_id']} [{active}] ({paused})")
        return dags
    else:
        print(f"Erro ao listar DAGs: {response.status_code}")
        print(response.text)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gatilho manual para DAGs do Airflow")
    parser.add_argument("--dag-id", help="ID do DAG a ser acionado")
    parser.add_argument("--list", action="store_true", help="Listar todos os DAGs disponíveis")
    parser.add_argument("--conf", help="Configuração JSON para passar ao DAG")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Nome de usuário para autenticação")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Senha para autenticação")
    
    args = parser.parse_args()
    
    if args.list:
        list_dags(username=args.username, password=args.password)
    elif args.dag_id:
        conf_dict = None
        if args.conf:
            try:
                conf_dict = json.loads(args.conf)
            except json.JSONDecodeError:
                print("Erro: O parâmetro 'conf' deve ser um JSON válido")
                exit(1)
        
        trigger_dag(args.dag_id, conf=conf_dict, username=args.username, password=args.password)
    else:
        parser.print_help()
