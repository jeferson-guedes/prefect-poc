from prefect import flow, task
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
import pandas as pd
import time
import random
import os

# Tarefas de ETL/Big Data - semelhantes ao que você já usa no Airflow

@task(name="extrair_dados_mysql", retries=3, log_prints=True)
def extrair_dados_mysql(tabela, limite=None):
    """
    Simula a extração de dados de um banco MySQL
    Em um caso real, usaríamos pymysql ou SQLAlchemy
    """
    print(f"Extraindo dados da tabela {tabela} do MySQL...")
    time.sleep(5)  # Simula uma consulta longa
    
    # Simula dados retornados do banco
    num_registros = limite or random.randint(1000, 10000)
    print(f"Extraídos {num_registros} registros da tabela {tabela}")
    
    # Gera um DataFrame simulado
    if tabela == "produtos":
        df = pd.DataFrame({
            "produto_id": [f"PROD-{i}" for i in range(1, num_registros + 1)],
            "nome": [f"Produto {i}" for i in range(1, num_registros + 1)],
            "categoria": [random.choice(["Roupas", "Eletrônicos", "Alimentos", "Móveis"]) for _ in range(num_registros)],
            "preco": [round(random.uniform(10.0, 1000.0), 2) for _ in range(num_registros)],
            "estoque": [random.randint(0, 100) for _ in range(num_registros)]
        })
    elif tabela == "pedidos":
        df = pd.DataFrame({
            "pedido_id": [f"PED-{i}" for i in range(1, num_registros + 1)],
            "cliente_id": [f"CLI-{random.randint(1, 1000)}" for _ in range(num_registros)],
            "data": [f"2023-{random.randint(1, 12)}-{random.randint(1, 28)}" for _ in range(num_registros)],
            "valor_total": [round(random.uniform(50.0, 5000.0), 2) for _ in range(num_registros)],
            "status": [random.choice(["Novo", "Processando", "Enviado", "Entregue", "Cancelado"]) for _ in range(num_registros)]
        })
    else:
        df = pd.DataFrame({"dummy": list(range(num_registros))})
    
    return df

@task(name="transformar_dados", log_prints=True)
def transformar_dados(df, tipo_transformacao):
    """
    Aplica transformações nos dados
    """
    print(f"Aplicando transformação '{tipo_transformacao}' em {len(df)} registros...")
    
    # Simula uma transformação pesada
    time.sleep(8)
    
    if tipo_transformacao == "enriquecimento":
        # Simula adição de novas colunas calculadas
        print("Adicionando colunas calculadas...")
        if "preco" in df.columns and "estoque" in df.columns:
            df["valor_estoque"] = df["preco"] * df["estoque"]
        
        if "categoria" in df.columns:
            # Simula enriquecimento com dados externos
            df["categoria_id"] = df["categoria"].map({
                "Roupas": "CAT-001",
                "Eletrônicos": "CAT-002",
                "Alimentos": "CAT-003",
                "Móveis": "CAT-004"
            })
    
    elif tipo_transformacao == "agregacao":
        # Simula agregação de dados
        print("Agregando dados...")
        if "categoria" in df.columns:
            df = df.groupby("categoria").agg({
                "preco": "mean",
                "estoque": "sum"
            }).reset_index()
            df = df.rename(columns={"preco": "preco_medio", "estoque": "estoque_total"})
            print(f"Dados agregados: {len(df)} registros após agregação")
    
    elif tipo_transformacao == "limpeza":
        # Simula limpeza de dados
        print("Limpando dados...")
        # Remove registros duplicados (simulado)
        registros_antes = len(df)
        df = df.iloc[0:int(len(df) * 0.9)]  # Simula remoção de 10% dos registros
        print(f"Limpeza: {registros_antes - len(df)} registros removidos")
    
    return df

@task(name="carregar_dados_redshift", retries=2, log_prints=True)
def carregar_dados_redshift(df, tabela_destino):
    """
    Simula o carregamento de dados no Redshift
    """
    print(f"Carregando {len(df)} registros na tabela {tabela_destino} do Redshift...")
    
    # Simula o tempo de carregamento (proporcional ao volume de dados)
    tempo_carga = len(df) * 0.001  # 1ms por registro (simulado)
    time.sleep(min(tempo_carga, 15))  # Limita a no máx 15 segundos para a demo
    
    print(f"Carga concluída! {len(df)} registros inseridos em {tabela_destino}")
    return {
        "tabela": tabela_destino,
        "registros_inseridos": len(df),
        "timestamp": time.time()
    }

@task(name="validar_dados_redshift", log_prints=True)
def validar_dados_redshift(resultado_carga):
    """
    Simula uma validação dos dados carregados
    """
    print(f"Validando dados carregados na tabela {resultado_carga['tabela']}...")
    time.sleep(3)
    
    # Simula validação bem-sucedida na maioria dos casos
    sucesso = random.random() > 0.1
    
    if sucesso:
        print(f"Validação bem-sucedida! Dados carregados corretamente em {resultado_carga['tabela']}")
        return True
    else:
        print(f"FALHA NA VALIDAÇÃO! Encontrados problemas nos dados de {resultado_carga['tabela']}")
        return False

# Fluxo ETL completo (produtos MySQL para Redshift)
@flow(name="ETL Produtos MySQL para Redshift", 
      description="Fluxo de ETL para carregar produtos do MySQL para o Redshift com transformações")
def etl_produtos_mysql_para_redshift(limite=None):
    # Extração
    df_produtos = extrair_dados_mysql("produtos", limite)
    
    # Transformação
    df_enriquecido = transformar_dados(df_produtos, "enriquecimento")
    df_agregado = transformar_dados(df_enriquecido, "agregacao")
    
    # Carga
    resultado_carga = carregar_dados_redshift(df_enriquecido, "produtos_dw")
    resultado_carga_agg = carregar_dados_redshift(df_agregado, "produtos_agg")
    
    # Validação
    validacao_ok = validar_dados_redshift(resultado_carga)
    validacao_agg_ok = validar_dados_redshift(resultado_carga_agg)
    
    return {
        "validacao_produtos": validacao_ok,
        "validacao_agregados": validacao_agg_ok,
        "total_registros": len(df_enriquecido),
        "total_agregados": len(df_agregado)
    }

# Fluxo ETL para pedidos (com transformações diferentes)
@flow(name="ETL Pedidos MySQL para Redshift")
def etl_pedidos_mysql_para_redshift(limite=None):
    # Extração
    df_pedidos = extrair_dados_mysql("pedidos", limite)
    
    # Transformação - neste caso apenas limpeza
    df_limpo = transformar_dados(df_pedidos, "limpeza")
    
    # Carga
    resultado_carga = carregar_dados_redshift(df_limpo, "pedidos_dw")
    
    # Validação
    validacao_ok = validar_dados_redshift(resultado_carga)
    
    return {
        "validacao_pedidos": validacao_ok,
        "total_registros": len(df_limpo)
    }

# Fluxo para migração completa de dados (executa os dois ETLs em sequência)
@flow(name="Migração Completa MySQL para Redshift", 
      description="Fluxo principal que coordena todos os ETLs do MySQL para o Redshift")
def migracao_completa_mysql_redshift():
    # Executa ETL de produtos
    resultado_produtos = etl_produtos_mysql_para_redshift()
    
    # Executa ETL de pedidos
    resultado_pedidos = etl_pedidos_mysql_para_redshift()
    
    # Retorna resumo da migração
    return {
        "produtos": resultado_produtos,
        "pedidos": resultado_pedidos,
        "sucesso_geral": resultado_produtos["validacao_produtos"] and resultado_pedidos["validacao_pedidos"]
    }

# Script para criar deployments
if __name__ == "__main__":
    # ETL de produtos (diário - meia-noite)
    produtos_deployment = Deployment.build_from_flow(
        flow=etl_produtos_mysql_para_redshift,
        name="etl-produtos-diario",
        work_queue_name="bigdata",
        schedule=CronSchedule(cron="0 0 * * *"),  # Meia-noite todos os dias
    )
    produtos_deployment.apply()
    
    # ETL de pedidos (diário - 01:00)
    pedidos_deployment = Deployment.build_from_flow(
        flow=etl_pedidos_mysql_para_redshift,
        name="etl-pedidos-diario",
        work_queue_name="bigdata",
        schedule=CronSchedule(cron="0 1 * * *"),  # 01:00 todos os dias
    )
    pedidos_deployment.apply()
    
    # Migração completa (semanal - domingo 03:00)
    migracao_deployment = Deployment.build_from_flow(
        flow=migracao_completa_mysql_redshift,
        name="migracao-completa-semanal",
        work_queue_name="bigdata",
        schedule=CronSchedule(cron="0 3 * * 0"),  # Domingo 03:00
    )
    migracao_deployment.apply()
    
    print("Cenário 3: Deployments de big data/ETL criados com sucesso!")
