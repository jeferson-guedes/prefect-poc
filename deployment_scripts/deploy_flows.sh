#!/bin/bash
set -e

# Aguarda o Prefect Server estar disponível
echo "Aguardando o Prefect Server ficar disponível..."
until curl -s http://prefect-server:4200/api/health > /dev/null; do
  sleep 2
done
echo "Prefect Server está disponível!"

# Cria os work pools necessários
# prefect work-pool create --type process scheduler-pool
prefect work-pool create scheduler-pool --type process --overwrite
# prefect work-pool create --type process worker-pool || true
# prefect work-pool create --type process bigdata-pool || true

# Implanta os fluxos de trabalho
echo "Implantando fluxos de trabalho..."
cd /app/flows

# Implanta os fluxos do cenário 1 (schedulers)
python -m cron.deploy_scheduler_flows

# Implanta os fluxos do cenário 2 (workers)
# python -m worker.deploy_worker_flows

# Implanta os fluxos do cenário 3 (bigdata)
# python -m bigdata.deploy_bigdata_flows

echo "Implantação de fluxos concluída com sucesso!"
