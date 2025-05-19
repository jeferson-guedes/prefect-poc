FROM prefecthq/prefect:3-latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl
# Instalação de dependências
RUN pip install prefect-aws prefect-docker boto3 pandas pymysql psycopg2-binary

# Copiar scripts de implantação de flows
COPY ./deployment_scripts /app/deployment_scripts

# Adicionar permissão de execução
RUN chmod +x /app/deployment_scripts/deploy_flows.sh

# Script para execução inicial
CMD ["/app/deployment_scripts/deploy_flows.sh"]
