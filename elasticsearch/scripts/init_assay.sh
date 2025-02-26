#!/bin/bash

ES_HOST=${ES_HOST:-localhost}
ES_PORT=${ES_PORT:-9200}
INDEX_NAME="assay_data"  
SLEEP_INTERVAL=${SLEEP_INTERVAL:-5}

# Wait for Elasticsearch to start
until curl -s http://${ES_HOST}:${ES_PORT} >/dev/null; do
  echo "Waiting for Elasticsearch to start at ${ES_HOST}:${ES_PORT}..."
  sleep 2
done

# Load all JSON files into Elasticsearch
for file in /usr/share/elasticsearch/assay_json/*.json; do
  FILENAME=$(basename "$file" .json)
  echo "Checking if $FILENAME already exists in Elasticsearch at http://${ES_HOST}:${ES_PORT}/${INDEX_NAME}/_doc/${FILENAME}"

  # Check if the document already exists
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://${ES_HOST}:${ES_PORT}/${INDEX_NAME}/_doc/${FILENAME}")
  if [ "$RESPONSE" -eq 200 ]; then
    echo "Document $FILENAME already exists. Skipping."
  else
    echo "Processing $file"

    # Call the Python script to process the JSON file
    python3 /usr/share/elasticsearch/scripts/process_assay.py "$file"

    echo "Loading $file into Elasticsearch"
    while true; do
      # Capture the full response body and status code
      FULL_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://${ES_HOST}:${ES_PORT}/${INDEX_NAME}/_doc/${FILENAME}" \
        -H "Content-Type: application/json" -d @"$file")
      RESPONSE_BODY=$(echo "$FULL_RESPONSE" | head -n 1)  # Get the response body
      RESPONSE_CODE=$(echo "$FULL_RESPONSE" | tail -n 1)  # Get the HTTP status code

      if [ "$RESPONSE_CODE" -eq 201 ]; then
        echo "Loaded $file successfully"
        break
      elif [ "$RESPONSE_CODE" -eq 429 ]; then
        echo "Rate limited. Waiting ${SLEEP_INTERVAL} seconds before retrying..."
        sleep ${SLEEP_INTERVAL}
      else
        echo "Failed to load $file. HTTP response code: $RESPONSE_CODE" >&2
        echo "Response body: $RESPONSE_BODY"  # Log the full response body
        break
      fi
    done
  fi
done
