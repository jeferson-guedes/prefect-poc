# Projeto de Migração para Prefect 2.0

Este projeto demonstra como migrar um sistema legado de processamento batch, schedulers e workers para o Prefect 2.0, abordando três cenários principais:

1. **Projeto de Cron (Schedulers)**: Migração de jobs cron para flows agendados no Prefect
2. **Projeto de Workers**: Processamento escalável horizontalmente de filas (RabbitMQ/SQS)
3. **Projeto de Big Data**: ETLs para migração de dados MySQL para Redshift

## Estrutura do Projeto

```
.
├── docker-compose.yml          # Configuração de todos os serviços
├── deployer.Dockerfile         # Dockerfile para implantar os flows automaticamente
├── deployment_scripts/         # Scripts para implantação automática
│   └── deploy_flows.sh         # Script de inicialização e implantação
├── flows/                      # Todos os flows do Prefect organizados por cenário
│   ├── cenario1/               # Fluxos para substituir tarefas cron
│   │   └── deploy_scheduler_flows.py
│   ├── cenario2/               # Fluxos para workers e processamento de filas
│   │   └── deploy_worker_flows.py
│   └── cenario3/               # Fluxos para ETL e big data
│       └── deploy_bigdata_flows.py
└── localstack-init/            # Scripts de inicialização para o LocalStack (SQS)
```

## Componentes do Sistema

### Infraestrutura
- **prefect-server**: Servidor API do Prefect com UI
- **postgres**: Banco de dados para o Prefect
- **rabbitmq**: Servidor RabbitMQ para simulação de filas
- **localstack**: Simula serviços AWS (SQS)

### Agents e Workers
- **prefect-agent-scheduler**: Para tarefas agendadas (substituindo cron)
- **prefect-agent-worker**: Para processamento escalável de filas
- **prefect-agent-bigdata**: Para ETL e tarefas pesadas

## Como Executar

1. Inicie todos os serviços:
   ```
   docker-compose up -d
   ```

2. Acesse a interface do Prefect:
   ```
   http://localhost:4200
   ```

3. Visualize os fluxos implantados e seus agendamentos

## Cenários Implementados

### Cenário 1: Substituição do Cron (scheduler)
- Tarefas agendadas para processamento de produtos
- Atualização diária de preços
- Executa em uma única máquina (não paralelizável)

### Cenário 2: Workers Escaláveis
- Processamento de filas RabbitMQ e SQS
- Escala horizontalmente conforme carga
- Tratamento de erros e retentativas
- Monitoramento de métricas de processamento

### Cenário 3: Big Data / ETL
- ETL de produtos do MySQL para Redshift
- ETL de pedidos do MySQL para Redshift
- Migração completa semanal
- Processamento de grandes volumes de dados

## Escalabilidade

Este projeto permite escalar workers horizontalmente, conforme necessário:

```bash
# Para escalar workers horizontalmente em produção:
docker-compose up -d --scale prefect-agent-worker=5
```

## Migração Gradual

Esta configuração foi projetada para permitir migração gradual:

1. Comece migrando alguns flows não críticos
2. Monitore o desempenho na UI do Prefect
3. Gradualmente migre mais flows à medida que ganha confiança

## Monitoramento e Observabilidade

Todos os flows incluem logs detalhados e métricas que podem ser visualizados na UI do Prefect. Para produção, considere adicionar:

- Prometheus para monitoramento
- Grafana para dashboards
- Trace distribuído (Jaeger/OpenTelemetry)

## Comparação com o Sistema Legado

| Aspecto | Sistema Legado | Prefect |
|---------|----------------|---------|
| Escalabilidade | Manual e limitada | Automática e dinâmica |
| Observabilidade | Inexistente | Logs, métricas e UI |
| Resiliência | Baixa, perdas de mensagens | Alta, com retentativas |
| Configuração | Fragmentada (cron, supervisor) | Unificada |
| Manutenção | Difícil, sem logs | Simples, com monitoramento |

## Próximos Passos

1. Migrar um flow por vez do sistema legado
2. Implementar monitoramento adicional
3. Configurar alertas
4. Implementar autoscaling baseado em métricas



Como usar:

Para listar todos os DAGs disponíveis:

```shell
python3 trigger_script.py --list
```


Para acionar um DAG específico:

```shell
python3 trigger_script.py --dag-id meu_dag_id
```

Para acionar um DAG com configurações personalizadas:
```shell
python3 trigger_script.py --dag-id meu_dag_id --conf '{"param1": "valor1", "param2": 123}'
```

O script também permite especificar credenciais diferentes, caso não esteja usando as padrões:

```shell
python3 trigger_script.py --dag-id meu_dag_id --username meuusuario --password minhasenha
```