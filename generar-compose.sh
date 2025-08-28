#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <archivo> <numero_de_clientes>"
    exit 1
fi

filename=$1
num_clients=$2

python3 generar-compose.py "$filename" "$num_clients"