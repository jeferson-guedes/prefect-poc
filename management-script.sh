#!/bin/bash
# Script utilitário para monitorar e gerenciar o ambiente Prefect

set -e

show_help() {
    echo "Prefect Environment Management Tool"
    echo ""
    echo "Uso: ./manage_env.sh [comando]"
    echo ""
    echo "Comandos:"
    echo "  start           Inicia todos os serviços"
    echo "  stop            Para todos os serviços"
    echo "  restart         Reinicia todos os serviços"
    echo "  status          Mostra o status dos serviços"
    echo "  logs [serviço]  Exibe logs do serviço especificado"
    echo "  scale [n]       Escala os workers para n instâncias"
    echo "  clean           Remove containers, volumes e networks"
    echo "  help            Exibe esta mensagem de ajuda"
    echo ""
    echo "Exemplos:"
    echo "  ./manage_env.sh start"
    echo "  ./manage_env.sh logs prefect-server"
    echo "  ./manage_env.sh scale 5"
}

start_services() {
    echo "Iniciando ambiente Prefect..."
    docker-compose up -d
    echo "Serviços iniciados. UI disponível em: http://localhost:4200"
}

stop_services() {
    echo "Parando serviços..."
    docker-compose down
    echo "Serviços parados."
}

restart_services() {
    echo "Reiniciando serviços..."
    docker-compose restart
    echo "Serviços reiniciados."
}

show_status() {
    echo "Status dos serviços:"
    docker-compose ps
}

show_logs() {
    service=$1
    if [ -z "$service" ]; then
        echo "Especifique um serviço para visualizar logs."
        echo "Serviços disponíveis:"
        docker-compose ps --services
        exit 1
    fi
    
    echo "Exibindo logs para $service..."
    docker-compose logs -f "$service"
}

scale_workers() {
    count=$1
    if [ -z "$count" ]; then
        echo "Especifique o número de instâncias para escalar."
        exit 1
    fi
    
    echo "Escalando workers para $count instâncias..."
    docker-compose up -d --scale prefect-agent-worker=$count
    echo "Workers escalados para $count instâncias."
}

clean_environment() {
    echo "Limpando ambiente..."
    docker-compose down -v
    echo "Ambiente limpo."
}

# Principal
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    scale)
        scale_workers "$2"
        ;;
    clean)
        clean_environment
        ;;
    help|*)
        show_help
        ;;
esac
