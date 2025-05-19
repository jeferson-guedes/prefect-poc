from prefect import flow, task
from prefect.deployments import Deployment
from prefect.task_runners import ConcurrentTaskRunner
import time
import random
import json

# Simulação de conexão com RabbitMQ e SQS
@task(name="conectar_rabbitmq", log_prints=True)
def conectar_rabbitmq():
    print("Conectando ao RabbitMQ...")
    time.sleep(1)
    # Em um caso real, usaríamos pika ou outra lib para conectar ao RabbitMQ
    return {"connection": "rabbitmq_simulado", "status": "connected"}

@task(name="conectar_sqs", log_prints=True)
def conectar_sqs():
    print("Conectando ao SQS...")
    time.sleep(1)
    # Em um caso real, usaríamos boto3 para conectar ao SQS
    return {"connection": "sqs_simulado", "status": "connected"}

@task(name="consumir_mensagens_fila", 
      retries=3, 
      retry_delay_seconds=30, 
      log_prints=True)
def consumir_mensagens_fila(conexao, num_mensagens=100):
    """
    Simula o consumo de mensagens de uma fila (RabbitMQ ou SQS)
    Em um cenário real, esse seria um worker escalável horizontalmente
    """
    print(f"Consumindo mensagens da fila usando {conexao['connection']}...")
    
    # Simula obtenção de mensagens
    mensagens = []
    for i in range(num_mensagens):
        # Simula diferentes tipos de mensagens
        tipo = random.choice(["produto", "pedido", "usuario"])
        id_entidade = random.randint(1000, 9999)
        
        mensagem = {
            "tipo": tipo,
            "id": f"{tipo.upper()}-{id_entidade}",
            "timestamp": time.time(),
            "dados": {
                "acao": random.choice(["criar", "atualizar", "deletar"]),
                "metadados": {
                    "origem": random.choice(["app", "site", "api"]),
                    "prioridade": random.choice(["alta", "media", "baixa"])
                }
            }
        }
        mensagens.append(mensagem)
        
    print(f"Consumidas {len(mensagens)} mensagens da fila.")
    return mensagens

@task(name="processar_mensagem", 
      retries=2, 
      retry_delay_seconds=10, 
      log_prints=True)
def processar_mensagem(mensagem):
    """
    Processa uma mensagem individual
    Esta tarefa será executada de forma concorrente para cada mensagem
    """
    print(f"Processando mensagem {mensagem['id']} do tipo {mensagem['tipo']}...")
    
    # Simula falha aleatória (para demonstrar retries)
    if random.random() < 0.05:
        raise Exception(f"Erro ao processar mensagem {mensagem['id']}")
    
    # Simula processamento com duração variável
    tempo_processamento = random.uniform(0.1, 0.5)
    time.sleep(tempo_processamento)
    
    resultado = {
        "mensagem_id": mensagem["id"],
        "processado_em": time.time(),
        "duracao": tempo_processamento,
        "status": "sucesso"
    }
    
    print(f"Mensagem {mensagem['id']} processada com sucesso em {tempo_processamento:.2f}s")
    return resultado

@task(name="salvar_resultados", log_prints=True)
def salvar_resultados(resultados):
    """
    Salva os resultados do processamento em um banco de dados
    """
    sucessos = len([r for r in resultados if r and r.get("status") == "sucesso"])
    falhas = len(resultados) - sucessos
    
    print(f"Resultados do processamento: {sucessos} sucessos, {falhas} falhas")
    print(f"Taxa de sucesso: {(sucessos / len(resultados) * 100):.2f}%")
    
    # Em um caso real, salvaríamos em um banco de dados
    return {
        "total": len(resultados),
        "sucessos": sucessos,
        "falhas": falhas
    }

@flow(name="Processamento de Fila RabbitMQ", 
      description="Consome e processa mensagens do RabbitMQ com escalabilidade horizontal",
      task_runner=ConcurrentTaskRunner())
def processar_fila_rabbitmq():
    """
    Fluxo para processar mensagens da fila RabbitMQ
    Usa ConcurrentTaskRunner para simular o processamento paralelo de mensagens
    """
    conexao = conectar_rabbitmq()
    
    # Em cenário real, configuração dinâmica baseada na fila
    num_mensagens = random.randint(50, 200)  # Simula carga variável
    
    print(f"Iniciando processamento de {num_mensagens} mensagens...")
    mensagens = consumir_mensagens_fila(conexao, num_mensagens)
    
    # Processa cada mensagem de forma concorrente
    resultados = []
    for mensagem in mensagens:
        # No Prefect 2.0, o map é implícito quando iteramos sobre uma coleção
        resultado = processar_mensagem(mensagem)
        resultados.append(resultado)
    
    metricas = salvar_resultados(resultados)
    return metricas

@flow(name="Processamento de Fila SQS", 
      description="Consome e processa mensagens do SQS da AWS com escalabilidade horizontal",
      task_runner=ConcurrentTaskRunner())
def processar_fila_sqs():
    """
    Fluxo para processar mensagens da fila SQS
    Similar ao fluxo RabbitMQ, mas para ilustrar a possibilidade de fluxos diferentes
    """
    conexao = conectar_sqs()
    
    # Em cenário real, configuração dinâmica baseada no tamanho da fila
    num_mensagens = random.randint(100, 500)  # SQS com mais mensagens neste exemplo
    
    print(f"Iniciando processamento de {num_mensagens} mensagens do SQS...")
    mensagens = consumir_mensagens_fila(conexao, num_mensagens)
    
    # Processa cada mensagem de forma concorrente
    resultados = []
    for mensagem in mensagens:
        resultado = processar_mensagem(mensagem)
        resultados.append(resultado)
    
    metricas = salvar_resultados(resultados)
    return metricas

# Script para criar deployments
if __name__ == "__main__":
    # Deployment para processamento de fila RabbitMQ (sem agendamento, acionado por API)
    rabbitmq_deployment = Deployment.build_from_flow(
        flow=processar_fila_rabbitmq,
        name="worker-rabbitmq",
        work_queue_name="worker",
        # Sem agendamento - acionado sob demanda ou por API
    )
    rabbitmq_deployment.apply()
    
    # Deployment para processamento de fila SQS (sem agendamento, acionado por API)
    sqs_deployment = Deployment.build_from_flow(
        flow=processar_fila_sqs,
        name="worker-sqs",
        work_queue_name="worker",
        # Sem agendamento - acionado sob demanda ou por API
    )
    sqs_deployment.apply()
    
    print("Cenário 2: Deployments de workers criados com sucesso!")
