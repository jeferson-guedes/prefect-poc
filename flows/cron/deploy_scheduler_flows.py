from prefect import flow, task, get_run_logger
from prefect.schedules import Cron
from prefect.filesystems import LocalFileSystem
from prefect.client.schemas.schedules import CronSchedule

import time
import random
import os



@task(name="processar_criacao_produto", 
      description="Processa a criação de produtos e notifica sistemas downstream",
      retries=3, 
      retry_delay_seconds=60)
def processar_criacao_produto(produto_id):
    """
    Simula o processamento de criação de produto e envio para outras filas
    """
    logger = get_run_logger()
    logger.info(f"Processando criação do produto {produto_id}")
    time.sleep(2)  # Simula processamento
    
    # Simulando falha aleatória (para demonstrar retries)
    if random.random() < 0.1:
        logger.error(f"Erro durante processamento do produto {produto_id}")
        raise Exception("Erro durante processamento do produto")
    
    # Simula envio para outra fila
    logger.info(f"Produto {produto_id} processado com sucesso e enviado para fila de validação")
    return produto_id

@task(name="validar_estoque", retries=2)
def validar_estoque(produto_id):
    """Valida o estoque de um produto"""
    logger = get_run_logger()
    logger.info(f"Validando estoque do produto {produto_id}")
    time.sleep(1)
    return {"produto_id": produto_id, "estoque_disponivel": random.randint(5, 100)}

@task(name="atualizar_catalogo")
def atualizar_catalogo(estoque_info):
    """Atualiza o catálogo de produtos"""
    logger = get_run_logger()
    logger.info(f"Atualizando catálogo para produto {estoque_info['produto_id']} com estoque {estoque_info['estoque_disponivel']}")
    time.sleep(1.5)
    return True

@flow(name="Fluxo de Criação de Produtos", 
      description="Fluxo que gerencia todo o ciclo de criação de produtos")
def fluxo_criacao_produtos():
    # Simula a criação de múltiplos produtos
    for i in range(1, 6):
        produto_id = f"PROD-{random.randint(1000, 9999)}"
        resultado = processar_criacao_produto(produto_id)
        if resultado:
            estoque = validar_estoque(resultado)
            atualizar_catalogo(estoque)

# Fluxo para atualização diária de preços (equivalente a uma tarefa de cron)
@task(name="obter_precos_atualizados")
def obter_precos_atualizados():
    print("Obtendo preços atualizados de fornecedores...")
    time.sleep(3)
    return [
        {"produto_id": f"PROD-{i}", "preco": round(random.uniform(10.0, 1000.0), 2)}
        for i in range(1000, 1010)
    ]

@task(name="atualizar_precos_sistema")
def atualizar_precos_sistema(precos):
    print(f"Atualizando {len(precos)} preços no sistema...")
    for preco in precos:
        print(f"Produto {preco['produto_id']} com novo preço: R$ {preco['preco']}")
        time.sleep(0.2)
    return True

@flow(name="Atualização Diária de Preços")
def fluxo_atualizacao_precos():
    precos = obter_precos_atualizados()
    atualizar_precos_sistema(precos)
    print("Atualização de preços concluída com sucesso!")

# Script que cria deployments para os fluxos
if __name__ == "__main__":
    local_storage = LocalFileSystem(basepath="/app/flows")
    local_storage.save(name="app-flows-storage", overwrite=True)

    entrypoint_path = "cron/deploy_scheduler_flows.py"

    fluxo_criacao_produtos.from_source(
        source=local_storage,
        entrypoint=f"{entrypoint_path}:fluxo_criacao_produtos"
    ).deploy(
        name="criacao-produtos-scheduled",
        work_pool_name="scheduler-pool",
        work_queue_name="cron", 
        cron="*/1 * * * *",
    )

    # fluxo_atualizacao_precos.deploy(
    #     name="atualizacao-precos-diaria",
    #     cron="0 2 * * *",  # Às 2:00 AM todos os dias
    #     work_pool_name="scheduler-pool",
    #     work_queue_name="cron"
    # )

    print("Cenário 1: Deployments de scheduler criados com sucesso!")
