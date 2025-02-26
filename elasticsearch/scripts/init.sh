#!/bin/bash

ES_HOST=${ES_HOST:-localhost}  # Default to localhost if ES_HOST is not set
ES_PORT=${ES_PORT:-9200}       # Default to port 9200 if ES_PORT is not set
INDEX_NAME=${INDEX_NAME:-test} # Default to index 'test' if INDEX_NAME is not set
SLEEP_INTERVAL=${SLEEP_INTERVAL:-5} # Default sleep interval between retries

# Wait for Elasticsearch to start
until curl -s http://${ES_HOST}:${ES_PORT} >/dev/null; do
  echo "Waiting for Elasticsearch to start at ${ES_HOST}:${ES_PORT}..."
  sleep 2
done

# Load all JSON files into Elasticsearch
for file in /usr/share/elasticsearch/output_json/*.json; do
  FILENAME=$(basename "$file" .json)
  echo "Checking if $FILENAME already exists in Elasticsearch at http://${ES_HOST}:${ES_PORT}/${INDEX_NAME}/_doc/${FILENAME}"

  # Check if the document already exists
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://${ES_HOST}:${ES_PORT}/${INDEX_NAME}/_doc/${FILENAME}")
  if [ "$RESPONSE" -eq 200 ]; then
    echo "Document $FILENAME already exists. Skipping."
  else
    echo "Processing $file"

    # Call the Python script to process the JSON file
    python3 /usr/share/elasticsearch/scripts/process_json.py "$file"

    echo "Loading $file into Elasticsearch"
    while true; do
      RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://${ES_HOST}:${ES_PORT}/${INDEX_NAME}/_doc/${FILENAME}" -H "Content-Type: application/json" -d @"$file")
      if [ "$RESPONSE" -eq 201 ]; then
        echo "Loaded $file successfully"
        break
      elif [ "$RESPONSE" -eq 429 ]; then
        echo "Rate limited. Waiting ${SLEEP_INTERVAL} seconds before retrying..."
        sleep ${SLEEP_INTERVAL}  # Wait before retrying
      else
        echo "Failed to load $file. HTTP response code: $RESPONSE" >&2
        break
      fi
    done
  fi
done
