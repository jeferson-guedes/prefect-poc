#!/usr/bin/env python
import json
import pika
import time
import random

# Configuração de conexão com RabbitMQ
connection_params = pika.ConnectionParameters(
    host='rabbitmq',
    port=5672,
    credentials=pika.PlainCredentials('user', 'password')
)

# Tipos de mensagens para geração de dados de exemplo
TIPOS_MENSAGENS = ['produto', 'pedido', 'usuario']
ACOES = ['criar', 'atualizar', 'deletar']
ORIGENS = ['app', 'site', 'api']
PRIORIDADES = ['alta', 'media', 'baixa']

def gerar_mensagem_aleatoria():
    """Gera uma mensagem aleatória no formato JSON"""
    tipo = random.choice(TIPOS_MENSAGENS)
    id_entidade = random.randint(1000, 9999)
    
    mensagem = {
        "tipo": tipo,
        "id": f"{tipo.upper()}-{id_entidade}",
        "timestamp": time.time(),
        "dados": {
            "acao": random.choice(ACOES),
            "metadados": {
                "origem": random.choice(ORIGENS),
                "prioridade": random.choice(PRIORIDADES)
            }
        }
    }
    return json.dumps(mensagem)

def main():
    tentativas = 0
    max_tentativas = 10
    
    # Tentativas de conexão com RabbitMQ (espera pela inicialização)
    while tentativas < max_tentativas:
        try:
            print(f"Tentando conectar ao RabbitMQ (tentativa {tentativas+1})...")
            connection = pika.BlockingConnection(connection_params)
            break
        except Exception as e:
            print(f"Falha na conexão: {e}")
            tentativas += 1
            time.sleep(5)
    
    if tentativas == max_tentativas:
        print("Não foi possível conectar ao RabbitMQ após várias tentativas.")
        return
    
    # Cria canal
    channel = connection.channel()
    
    # Declara filas
    filas = ['produto-fila', 'pedido-fila', 'usuario-fila']
    for fila in filas:
        channel.queue_declare(queue=fila, durable=True)
    
    # Preenche filas com mensagens de exemplo
    total_mensagens = 0
    for _ in range(50):  # Gera 50 lotes de mensagens
        for fila in filas:
            # Número aleatório de mensagens por lote
            num_mensagens = random.randint(10, 50)
            
            for _ in range(num_mensagens):
                mensagem = gerar_mensagem_aleatoria()
                channel.basic_publish(
                    exchange='',
                    routing_key=fila,
                    body=mensagem,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Torna a mensagem persistente
                    )
                )
            
            total_mensagens += num_mensagens
            print(f"Enviadas {num_mensagens} mensagens para a fila: {fila}")
    
    print(f"Total de {total_mensagens} mensagens enviadas para as filas RabbitMQ")
    
    # Fecha conexão
    connection.close()

if __name__ == "__main__":
    # Espera o RabbitMQ inicializar
    time.sleep(15)
    main()
