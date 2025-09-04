#!/bin/bash

# Script para validar el funcionamiento del echo server
# Uso: ./validar-echo-server.sh

# Configuración
ECHO_SERVER_HOST="server"
ECHO_SERVER_PORT="12345"
TEST_MESSAGE="test_message_$(date +%s)"
TIMEOUT=5

# Función para limpiar recursos
cleanup() {
    if [ ! -z "$CONTAINER_ID" ]; then
        docker rm -f "$CONTAINER_ID" >/dev/null 2>&1
    fi
}

# Configurar trap para limpiar en caso de error
trap cleanup EXIT

# Ejecutar test usando netcat en un container temporal
# Conectamos al container a la red testing_net del proyecto tp0
CONTAINER_ID=$(docker run -d --rm \
    --network "tp0_testing_net" \
    nicolaka/netshoot \
    tail -f /dev/null)

if [ -z "$CONTAINER_ID" ]; then
    echo "action: test_echo_server | result: fail"
    exit 1
fi

# Enviar mensaje y capturar respuesta
RESPONSE=$(docker exec "$CONTAINER_ID" bash -c "
    echo '$TEST_MESSAGE' | timeout $TIMEOUT nc $ECHO_SERVER_HOST $ECHO_SERVER_PORT 2>/dev/null
" 2>/dev/null)

# Validar respuesta
if [ "$RESPONSE" = "$TEST_MESSAGE" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi