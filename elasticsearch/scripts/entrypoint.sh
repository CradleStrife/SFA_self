#!/bin/bash

echo "Starting entrypoint script..."

# Run Eureka client initialization
echo "Running Eureka client initialization..."
python3 /usr/share/elasticsearch/init_es.py
if [ $? -eq 0 ]; then
  echo "Eureka client initialized successfully."
else
  echo "Failed to initialize Eureka client."
  exit 1
fi

# Start Elasticsearch
echo "Starting Elasticsearch..."
exec /usr/local/bin/docker-entrypoint.sh elasticsearch
