# Use the official Elasticsearch image
FROM docker.elastic.co/elasticsearch/elasticsearch:8.13.4

# Set environment variables for Elasticsearch
# ENV discovery.type=single-node


# Copy initialization script to a writable directory
COPY scripts/init.sh /usr/share/elasticsearch/init.sh
COPY scripts/init_assay.sh /usr/share/elasticsearch/init_assay.sh
COPY scripts/init_es.py /usr/share/elasticsearch/init_es.py
COPY scripts/entrypoint.sh /usr/share/elasticsearch/entrypoint.sh
COPY scripts/process_json.py /usr/share/elasticsearch/process_json.py
COPY scripts/process_assay.py /usr/share/elasticsearch/process_assay.py

# # Copy all JSON data files
COPY output_json /usr/share/elasticsearch/output_json
COPY assay_json /usr/share/elasticsearch/assay_json
USER root
RUN chmod +x /usr/share/elasticsearch/entrypoint.sh
# RUN chmod +x /usr/share/elasticsearch/init.sh
# RUN chmod +x /usr/share/elasticsearch/init_assay.sh
# RUN chmod +x /usr/share/elasticsearch/process_json.py
# RUN chmod +x /usr/share/elasticsearch/process_assay.py
# RUN chmod -R 777 /usr/share/elasticsearch/output_json
# RUN chmod -R 777 /usr/share/elasticsearch/assay_json
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install requests py_eureka_client
USER elasticsearch
ENTRYPOINT ["/usr/share/elasticsearch/entrypoint.sh"]


# Expose necessary ports
EXPOSE 9200 9300

