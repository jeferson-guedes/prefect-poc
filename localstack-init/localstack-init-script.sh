#!/bin/bash
# Script para criar filas SQS no LocalStack durante a inicialização

# Aguardar a inicialização do serviço LocalStack
sleep 10

# Configurar AWS CLI para LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:4566

# Criar filas SQS
echo "Criando filas SQS..."
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name produto-fila
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name pedido-fila
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name usuario-fila

# Verificar filas criadas
echo "Filas SQS criadas:"
aws --endpoint-url=http://localhost:4566 sqs list-queues

echo "Inicialização do LocalStack concluída!"
