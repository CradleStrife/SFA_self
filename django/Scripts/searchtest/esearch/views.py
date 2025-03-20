from django.http import HttpResponse, JsonResponse
# from .es_call import esearch (assay information)
from .es_call import *
from elasticsearch import Elasticsearch
from django.conf import settings
import re
from collections import Counter
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import time
from datetime import datetime
from elasticsearch_dsl.utils import AttrList
import os
from django.core.cache import cache
from celery import shared_task
from django.core.cache import cache
from .utili import get_elasticsearch_client
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures
from esearch.models import TempData
#LARRY
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
##Frank
from .Excel2Json import excel2jsons
import threading
from elasticsearch_dsl import Search, Q


# <--------------------------------------------LOCAL DATA SET------------------------------------------------------>
logger = logging.getLogger(__name__)

@csrf_exempt
def clear_cache(request):
    cache.clear()
    return HttpResponse("Cache cleared")

@csrf_exempt
def simple_search(request):
    index_name=request.GET.get('index_name')
    field_name=request.GET.get('field_name')
    field_value=request.GET.get('field_value')
    results=esearch_simple(index_name,field_name,field_value)
    # # print("index_name:",index_name)
    # # print("field_name:",field_name)
    # # print("field_value:",field_value)
    # # print(results)
    response_data={
        'results':results,
        'count':len(results)
    }
    return JsonResponse(response_data,safe=False)

@csrf_exempt
def search_index(request):
    start_time = time.time()
    # Collect query parameters
    params = request.GET.dict()

    # Set default values for specific parameters
    params['serotype_condition'] = params.get('serotype_condition', '')
    params['source_condition'] = params.get('source_condition', '')
    params['required_data'] = params.get('required_data', '')
    params['start_date'] = params.get('start_date', '')
    params['end_date'] = params.get('end_date', '')
    params['index'] = params.get('index', settings.INDEX_NAME)

    if (params['index'] == 'assay_data') or ("assay_index_name" in params):
        params['assay_index_name']=params.get('assay_index_name','salmonella-assay-index-v4')
        index_name=params['assay_index_name']

    print("params:",params)
    # params['assay_index_name']=params.get('assay_index_name','campylobactor-assay-index')
    # Filter out empty parameters, but exclude the 'index' key from being passed to Elasticsearch
    search_params = {k: v for k, v in params.items() if v and k != 'index'}
    print("search params:",search_params)
    # Use the index to decide which search function to use
    if params['index'] == 'assay_data':
        # print('b')
        results = esearch_assay(**search_params)
        
    else:
        results = esearch_local(**search_params)
        # print('a')

    response_data = {
        'results': results,
        'count': len(results)
    }

    # Conditionally call functions based on required_data
    # params['start_date']='1902'
    # params['end_date']='2024'
    max_workers = os.cpu_count() or 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = []
        cache_key_suffix = f"{params.get('start_date', '')}_{params.get('end_date', '')}"
        cache_key_suffix2 = f"{params.get('start_date', '')}_{params.get('end_date', '')}_{params.get('Serotype', '')}_{params.get('Source', '')}"
        cache_key_suffix3 = f"{params.get('start_date', '')}_{params.get('end_date', '')}_{params.get('serotype', '')}_{params.get('isolate_source', '')}"
        required_data = params.get('required_data', '').split(',')
        # print("start", required_data)
        if 'serotypes' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'serotypes', process_serotypes, params['start_date'], params['end_date']))

        if 'serotype' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'serotype', process_serotypes_assay, params['start_date'], params['end_date'],index_name=index_name))

        if 'mlst' in required_data:                            
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'mlst', process_mlst, params['start_date'], params['end_date']))

        if 'mlst_a' in required_data: 
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'mlst_a', process_mlst_assay, params['start_date'], params['end_date'],index_name=index_name))

        if 'sourcetype' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'sourcetype', process_source, params['start_date'], params['end_date']))

        if 'isolate_source' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'isolate_source', process_source_assay, params['start_date'], params['end_date'],index_name=index_name))


        if 'country_counts' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'country_counts', fetch_country_counts, params['start_date'], params['end_date']))

        if 'sero_MLST' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'sero_MLST', process_sero_MLST, params['start_date'], params['end_date']))

        if 'country_sero' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'country_sero', country_serotype, params['start_date'], params['end_date']))

        if 'geo_location' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix2, 'geo_location', geo_dis, params['start_date'], params['end_date'], params['Serotype'], params['Source'], params['serotype_condition'], params['source_condition']))
        
        if 'geo_location_a' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix3, 'geo_location_a', geo_dis_assay, params['start_date'], params['end_date'], params['serotype'], params['isolate_source'], params['serotype_condition'], params['source_condition'],index_name=index_name))

        if 'process_country_sourcedata' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_country_sourcedata', process_country_source, params['start_date'], params['end_date']))
        
        if 'process_country_sourcedata_a' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_country_sourcedata_a', process_country_source_a, params['start_date'], params['end_date'],index_name=index_name))
        
        if 'process_mlst_tabledata_a' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_mlst_tabledata_a', process_mlst_table_a, params['start_date'], params['end_date'],index_name=index_name))
        
        if 'process_mlst_tabledata' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_mlst_tabledata', process_mlst_table, params['start_date'], params['end_date']))

        if 'process_ID_serodata' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_serodata', process_ID_sero, params['start_date'], params['end_date']))

        if 'process_ID_serodata_a' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_serodata_a', process_ID_sero_a, params['start_date'], params['end_date'],index_name=index_name))

        if 'process_ID_MLSTdata' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_MLSTdata', process_ID_MLST, params['start_date'], params['end_date']))

        if 'process_ID_MLSTdata_a' in required_data:
            tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_MLSTdata_a', process_ID_MLST_a, params['start_date'], params['end_date'],index_name=index_name))

        

        for task in as_completed(tasks):
            result = task.result()

            key, data = result
            response_data[key] = data
           
        
        end_time = time.time()  # End time
        total_time = end_time - start_time
        # # print(f"search_index processing time: {total_time:.2f} seconds")
        # # print(response_data)
    
    return JsonResponse(response_data, safe=False, json_dumps_params={'default': str})

@csrf_exempt
def search_index_clustering(request):
    start_time = time.time()
    # Collect query parameters
    params = request.GET.dict()

    # Set default values for specific parameters
    # params['ID'] = params.get('ID', '')
    # params['Source'] = params.get('Source', '')
    # params['Date'] = params.get('Date', '')
    # params['Country'] = params.get('Country', '')
    # params['Brand'] = params.get('Brand', '')
    # params['Serotype'] = params.get('Serotype', '')
    # params['serotype_condition'] = params.get('serotype_condition', '')
    # params['source_condition'] = params.get('source_condition', '')
    # params['required_data'] = params.get('required_data', '')
    # params['start_date'] = params.get('start_date', '')
    # params['end_date'] = params.get('end_date', '')
    # params['index'] = params.get('index', '')  # index 参数由前端传递

    # params['assay_index_name']=params.get('assay_index_name','salmonella-assay-index-v4')

    # Filter out empty parameters, but exclude the 'index' and 'required_data' keys from being passed to Elasticsearch
    search_params = {k: v for k, v in params.items() if v and k not in ['index', 'required_data', 'index_names']}

    results = []
    index_names=params['index_names'].split(',')
    for index_name in index_names:
        if index_name=='local':
            print("index_name:","local")
            results+=esearch_local_clustering(**search_params)
            print(len(results))
        else:
            assay_search_params=search_params.copy()
            assay_search_params['assay_index_name']=index_name
            results+=esearch_assay_clustering(**assay_search_params)
    
    # 根据 index 参数决定使用哪个搜索函数
    # if params['index'] == 'both':
    #     # 如果选择了 both，则从两个数据存储中检索数据
    #     results_local = esearch_local_clustering(**search_params)
    #     results_assay = esearch_assay(**search_params)
    #     results = results_local + results_assay
    # elif params['index'] == 'assay_data':
    #     results = esearch_assay(**search_params)
    # else:
    #     results = esearch_local_clustering(**search_params)

    print(len(results))
    # results = esearch_local_clustering(**search_params)
    # 处理结果，确保数据格式正确
    processed_results = []
    for item in results:
        processed_item = {
            'ID': item.get('ID', []),
            'Source': item.get('Source', []),
            'Date': item.get('Date', []),
            'Country': item.get('Country', []),
            'Brand': item.get('Brand', []),
            'Serotype': item.get('Serotype', []),
            'MLST': item.get('MLST', []),
            'AST': item.get('AST', []),
            'SPI': item.get('SPI', []),
            'AMR': item.get('AMR', []),
            'plasmid': item.get('plasmid', []),
            # Include other necessary attributes
            "index_name": item.get("index_name", ""),
        }

        # Ensure 'AST', 'SPI', 'AMR', 'plasmid' are in list format
        for field in ['AST', 'SPI', 'AMR', 'plasmid']:
            if processed_item[field]:
                if isinstance(processed_item[field], dict):
                    processed_item[field] = [processed_item[field]]
                elif not isinstance(processed_item[field], list):
                    processed_item[field] = [processed_item[field]]
            else:
                processed_item[field] = []

        processed_results.append(processed_item)

    response_data = {
        'results': processed_results,
        'count': len(processed_results)
    }

    # Conditionally call functions based on required_data
    # max_workers = os.cpu_count() or 1
    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     tasks = []
    #     cache_key_suffix = f"{params.get('start_date', '')}_{params.get('end_date', '')}"
    #     cache_key_suffix2 = f"{params.get('start_date', '')}_{params.get('end_date', '')}_{params.get('Serotype', '')}_{params.get('Source', '')}"
    #     cache_key_suffix3 = f"{params.get('start_date', '')}_{params.get('end_date', '')}_{params.get('serotype', '')}_{params.get('isolate_source', '')}"
    #     required_data = params.get('required_data', '').split(',')
    #     # print("start", required_data)
    #     if 'serotypes' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'serotypes', process_serotypes, params['start_date'], params['end_date']))

    #     if 'serotype' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'serotype', process_serotypes_assay, params['start_date'], params['end_date']))

    #     if 'mlst' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'mlst', process_mlst, params['start_date'], params['end_date']))

    #     if 'mlst_a' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'mlst_a', process_mlst_assay, params['start_date'], params['end_date']))

    #     if 'sourcetype' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'sourcetype', process_source, params['start_date'], params['end_date']))

    #     if 'isolate_source' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'isolate_source', process_source_assay, params['start_date'], params['end_date']))

    #     if 'country_counts' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'country_counts', fetch_country_counts, params['start_date'], params['end_date']))

    #     if 'sero_MLST' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'sero_MLST', process_sero_MLST, params['start_date'], params['end_date']))

    #     if 'country_sero' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'country_sero', country_serotype, params['start_date'], params['end_date']))

    #     if 'geo_location' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix2, 'geo_location', geo_dis, params['start_date'], params['end_date'], params['Serotype'], params['Source'], params['serotype_condition'], params['source_condition']))

    #     if 'geo_location_a' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix3, 'geo_location_a', geo_dis_assay, params['start_date'], params['end_date'], params['serotype'], params['isolate_source'], params['serotype_condition'], params['source_condition']))

    #     if 'process_country_sourcedata' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_country_sourcedata', process_country_source, params['start_date'], params['end_date']))

    #     if 'process_country_sourcedata_a' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_country_sourcedata_a', process_country_source_a, params['start_date'], params['end_date']))

    #     if 'process_mlst_tabledata_a' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_mlst_tabledata_a', process_mlst_table_a, params['start_date'], params['end_date']))

    #     if 'process_mlst_tabledata' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_mlst_tabledata', process_mlst_table, params['start_date'], params['end_date']))

    #     if 'process_ID_serodata' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_serodata', process_ID_sero, params['start_date'], params['end_date']))

    #     if 'process_ID_serodata_a' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_serodata_a', process_ID_sero_a, params['start_date'], params['end_date']))

    #     if 'process_ID_MLSTdata' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_MLSTdata', process_ID_MLST, params['start_date'], params['end_date']))

    #     if 'process_ID_MLSTdata_a' in required_data:
    #         tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_MLSTdata_a', process_ID_MLST_a, params['start_date'], params['end_date']))

    #     for task in as_completed(tasks):
    #         result = task.result()
    #         key, data = result
    #         response_data[key] = data

    end_time = time.time()  # End time
    total_time = end_time - start_time
    # # print(f"search_index processing time: {total_time:.2f} seconds")
    # # print(response_data)

    return JsonResponse(response_data, safe=False, json_dumps_params={'default': str})

# def search_index(request):
#     start_time = time.time()
#     # Collect query parameters
#     params = request.GET.dict()

#     # Set default values for specific parameters
#     params['ID'] = params.get('ID', '')
#     params['Source'] = params.get('Source', '')
#     params['Date'] = params.get('Date', '')
#     params['Country'] = params.get('Country', '')
#     params['Brand'] = params.get('Brand', '')
#     params['Serotype'] = params.get('Serotype', '')
#     params['serotype_condition'] = params.get('serotype_condition', '')
#     params['source_condition'] = params.get('source_condition', '')
#     params['required_data'] = params.get('required_data', '')
#     params['start_date'] = params.get('start_date', '')
#     params['end_date'] = params.get('end_date', '')
#     params['index'] = params.get('index', '')  # index 参数由前端传递

#     # Filter out empty parameters, but exclude the 'index' and 'required_data' keys from being passed to Elasticsearch
#     search_params = {k: v for k, v in params.items() if v and k not in ['index', 'required_data']}

#     results = []

#     # 根据 index 参数决定使用哪个搜索函数
#     if params['index'] == 'both':
#         # 如果选择了 both，则从两个数据存储中检索数据
#         results_local = esearch_local(**search_params)
#         results_assay = esearch_assay(**search_params)
#         results = results_local + results_assay
#     elif params['index'] == 'assay_data':
#         results = esearch_assay(**search_params)
#     else:
#         results = esearch_local(**search_params)

#     # 处理结果，确保数据格式正确
#     processed_results = []
#     for item in results:
#         processed_item = {
#             'ID': item.get('ID', []),
#             'Source': item.get('Source', []),
#             'Date': item.get('Date', []),
#             'Country': item.get('Country', []),
#             'Brand': item.get('Brand', []),
#             'Serotype': item.get('Serotype', []),
#             'MLST': item.get('MLST', []),
#             'AST': item.get('AST', []),
#             'SPI': item.get('SPI', []),
#             'AMR': item.get('AMR', []),
#             'plasmid': item.get('plasmid', []),
#             # Include other necessary attributes
#         }

#         # Ensure 'AST', 'SPI', 'AMR', 'plasmid' are in list format
#         for field in ['AST', 'SPI', 'AMR', 'plasmid']:
#             if processed_item[field]:
#                 if isinstance(processed_item[field], dict):
#                     processed_item[field] = [processed_item[field]]
#                 elif not isinstance(processed_item[field], list):
#                     processed_item[field] = [processed_item[field]]
#             else:
#                 processed_item[field] = []

#         processed_results.append(processed_item)

#     response_data = {
#         'results': processed_results,
#         'count': len(processed_results)
#     }

#     # Conditionally call functions based on required_data
#     max_workers = os.cpu_count() or 1
#     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#         tasks = []
#         cache_key_suffix = f"{params.get('start_date', '')}_{params.get('end_date', '')}"
#         cache_key_suffix2 = f"{params.get('start_date', '')}_{params.get('end_date', '')}_{params.get('Serotype', '')}_{params.get('Source', '')}"
#         cache_key_suffix3 = f"{params.get('start_date', '')}_{params.get('end_date', '')}_{params.get('serotype', '')}_{params.get('isolate_source', '')}"
#         required_data = params.get('required_data', '').split(',')
#         # print("start", required_data)
#         if 'serotypes' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'serotypes', process_serotypes, params['start_date'], params['end_date']))

#         if 'serotype' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'serotype', process_serotypes_assay, params['start_date'], params['end_date']))

#         if 'mlst' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'mlst', process_mlst, params['start_date'], params['end_date']))

#         if 'mlst_a' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'mlst_a', process_mlst_assay, params['start_date'], params['end_date']))

#         if 'sourcetype' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'sourcetype', process_source, params['start_date'], params['end_date']))

#         if 'isolate_source' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'isolate_source', process_source_assay, params['start_date'], params['end_date']))

#         if 'country_counts' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'country_counts', fetch_country_counts, params['start_date'], params['end_date']))

#         if 'sero_MLST' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'sero_MLST', process_sero_MLST, params['start_date'], params['end_date']))

#         if 'country_sero' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'country_sero', country_serotype, params['start_date'], params['end_date']))

#         if 'geo_location' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix2, 'geo_location', geo_dis, params['start_date'], params['end_date'], params['Serotype'], params['Source'], params['serotype_condition'], params['source_condition']))

#         if 'geo_location_a' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix3, 'geo_location_a', geo_dis_assay, params['start_date'], params['end_date'], params['serotype'], params['isolate_source'], params['serotype_condition'], params['source_condition']))

#         if 'process_country_sourcedata' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_country_sourcedata', process_country_source, params['start_date'], params['end_date']))

#         if 'process_country_sourcedata_a' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_country_sourcedata_a', process_country_source_a, params['start_date'], params['end_date']))

#         if 'process_mlst_tabledata_a' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_mlst_tabledata_a', process_mlst_table_a, params['start_date'], params['end_date']))

#         if 'process_mlst_tabledata' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_mlst_tabledata', process_mlst_table, params['start_date'], params['end_date']))

#         if 'process_ID_serodata' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_serodata', process_ID_sero, params['start_date'], params['end_date']))

#         if 'process_ID_serodata_a' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_serodata_a', process_ID_sero_a, params['start_date'], params['end_date']))

#         if 'process_ID_MLSTdata' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_MLSTdata', process_ID_MLST, params['start_date'], params['end_date']))

#         if 'process_ID_MLSTdata_a' in required_data:
#             tasks.append(executor.submit(get_or_process, cache_key_suffix, 'process_ID_MLSTdata_a', process_ID_MLST_a, params['start_date'], params['end_date']))

#         for task in as_completed(tasks):
#             result = task.result()
#             key, data = result
#             response_data[key] = data

#     end_time = time.time()  # End time
#     total_time = end_time - start_time
#     # # print(f"search_index processing time: {total_time:.2f} seconds")
#     # # print(response_data)

#     return JsonResponse(response_data, safe=False, json_dumps_params={'default': str})


def get_or_process(cache_key_suffix, cache_key_prefix, process_func, *args, index_name=None):
    cache_key = f'{cache_key_prefix}_{cache_key_suffix}'
    if index_name:
        cache_key = f'{cache_key_prefix}_{index_name}_{cache_key_suffix}'
    data = cache.get(cache_key)
    # print(cache_key)

    # Pass index_name to the process function if it's provided
    if not data:
    # if True:
        if index_name:
            data = process_func(*args, index_name=index_name)
        else:
            data = process_func(*args)
        
        cache.set(cache_key, data, timeout=60*60)  # Cache timeout of 1 hour

    # print("data",data)
    return cache_key_prefix, data


@csrf_exempt
def update_document(request): 
    es = get_elasticsearch_client()
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doc_id = data.get('ID')            
            if isinstance(doc_id, str):
                    doc_id = doc_id.replace("[", "").replace("]", "").replace("'", "").strip()
                    doc_id= doc_id[2:]
                    doc_id = doc_id.lstrip('0')
                    # print(doc_id)
            if 'Date' in data and isinstance(data['Date'], str):
                data['Date'] = [data['Date']]
            if 'Country' in data and isinstance(data['Country'], str):
                data['Country'] = [data['Country']]
            if 'AST' in data :
                data['AST']=[data['AST']]
            script = {
                "source": "; ".join([f"ctx._source.{key} = params.{key}" for key in data.keys()]),
                "lang": "painless",
                "params": data
            }
            # Update the document in Elasticsearch
            response = es.update(index=settings.INDEX_NAME, id=doc_id, body={"script": script})
            return JsonResponse({'status': 'success', 'response': response.body}, status=200)
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    
def recursive_date_check(data):
    if isinstance(data, list):
        return [recursive_date_check(item) for item in data]
    elif isinstance(data, dict):
        return {key: recursive_date_check(value) for key, value in data.items()}
    elif data == 'NaT':
        return '1900-01-01'
    return data

@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
        es = get_elasticsearch_client()
        index_name = settings.INDEX_NAME
        files = request.FILES.getlist('files')
        results = []

        if len(files) == 1:
            file = files[0]
            file_content = file.read().decode('utf-8')
            try:
                json_data = json.loads(file_content)
            except json.JSONDecodeError:
                return JsonResponse({'error': f"File {file.name} is corrupted and could not be uploaded"}, status=400)
            
            file_name = os.path.splitext(file.name)[0]

            # Check if the document already exists
            response = es.exists(index=index_name, id=file_name)
            if response:
                return JsonResponse({'error': f"File {file.name} already exists"}, status=400)

            # Recursively check and modify the 'Date' field if necessary
            json_data = recursive_date_check(json_data)

            # Index the document if it does not exist
            response = es.index(index=index_name, id=file_name, document=json_data)
            if response['result'] != 'created':
                return JsonResponse({'error': f"Failed to upload {file.name}"}, status=500)
            
            return JsonResponse({'message': 'File uploaded successfully'}, status=200)
        
        else:
            all_exist = True
            for file in files:
                file_name = os.path.splitext(file.name)[0]
                response = es.exists(index=index_name, id=file_name)
                if not response:
                    all_exist = False
                    break
            
            if all_exist:
                return JsonResponse({'error': 'All files already exist'}, status=400)
            
            for file in files:
                file_content = file.read().decode('utf-8')
                try:
                    json_data = json.loads(file_content)
                except json.JSONDecodeError:
                    results.append({'file': file.name, 'status': 'failed', 'message': 'File is corrupted and could not be uploaded'})
                    continue
                
                file_name = os.path.splitext(file.name)[0]

                # Recursively check and modify the 'Date' field if necessary
                json_data = recursive_date_check(json_data)
 
                # Index the document if it does not exist
                response = es.index(index=index_name, id=file_name, document=json_data)
                if response['result'] != 'created':
                    results.append({'file': file.name, 'status': 'failed', 'message': 'Failed to upload'})
                else:
                    results.append({'file': file.name, 'status': 'success', 'message': 'Uploaded successfully'})
            
            return JsonResponse({'results': results}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)







########################################################################################

# HuHan!!!!!
lock2temp=threading.Lock()

@csrf_exempt
def upload2temp(request):
    if request.method == 'POST':
        es = get_elasticsearch_client()
        index_name = settings.INDEX_NAME
        files = request.FILES.getlist('files')
        results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for file in files:
                # print(file.name)
                if file.name.endswith('.json'):
                    file_content = file.read().decode('utf-8')
                    try:
                        json_data = json.loads(file_content)
                    except json.JSONDecodeError:
                        lock2temp.acquire()
                        results.append({'file': file.name, 'status': 'failed', 'message': 'File is corrupted and could not be uploaded'})
                        lock2temp.release()
                        continue
                    future=executor.submit(process_single_json2temp,json_data,file,results)
                    futures.append(future)
                elif file.name.endswith('.xlsx'):
                    # print("xlsx")
                    try:
                        json_datas=excel2jsons(file)
                        for json_data in json_datas:
                            future=executor.submit(process_single_json2temp,json_data,file,results)
                            futures.append(future)
                    except Exception as e:
                        lock2temp.acquire()
                        results.append({'file': file.name, ' status': 'failed', ' message': str(e)})
                        lock2temp.release()

            # 等待所有任务完成
            for future in futures:
                future.result()           
        return JsonResponse({'results': results}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def process_single_json2temp(json_data,file,results):
    json_data = recursive_date_check(json_data)
    if uploadOne2temp(json_data['ID'][0],json_data):
        lock2temp.acquire()
        results.append({'file': file.name, ' status': 'success', 'message': 'Uploaded successfully'})
        lock2temp.release()
    else:
        lock2temp.acquire()
        results.append({'file': file.name, ' status': 'failed', ' message': 'File already exists'})
        lock2temp.release()

def uploadOne2temp(file_name, json_content):
    json_id=json_content['ID'][0]
    if TempData.objects.filter(fileName=file_name).exists() or TempData.objects.filter(jsonId=json_id).exists():
        return False
    fileObj=TempData.objects.create(fileName=file_name, jsonId=json_id, jsonContent=json.dumps(json_content))
    # print(fileObj.jsonId," uploaded")
    return True









lockGetTemp=threading.Lock()
def getOneTempDataJob(fileObj,results):
    # # print(f"Processing file: {fileObj.fileName}")  # 打印文件名
    try:
        # 將 JSON 字符串轉換為字典
        hit = json.loads(fileObj.jsonContent)
        # # print(f"File content: {hit}")  # 打印文件内容
    except json.JSONDecodeError as e:
        # # print(f"JSON Decode Error for {fileObj.fileName}: {str(e)}")
        return
    
    # 初始化 AST 格式化處理
    formatted_ast = hit.get("AST", {})
    if formatted_ast == "NA":
        formatted_ast = {"NA": "NA"}
    elif isinstance(formatted_ast, list):
        formatted_ast = {str(i): item for i, item in enumerate(formatted_ast)}  # 簡單轉換列表為字典
    
    # 提取其他字段，確保字段存在
    Date = hit.get("Date", ["Unknown"])[0]  # 假設 Date 是列表
    Country = hit.get("Country", ["Unknown"])[0]
    AST_a = formatted_ast

    # 構造結果元組
    result_tuple = (
        
        hit.get("ID", "N/A"),
        hit.get("Source", "N/A"),
        Date,
        Country,
        hit.get("Brand", "N/A"),
        hit.get("Serotype", "N/A"),
        hit.get("MLST", "N/A"),
        AST_a,
        hit.get("SPI", "N/A"),
        hit.get("AMR", "N/A"),
        hit.get("plasmid", "N/A"),

        fileObj.fileName,
    )
    lockGetTemp.acquire()
    results.append(result_tuple)
    lockGetTemp.release()


# EDITED
@csrf_exempt
def getTempData(request):
    try:
        results = []
        # print("Fetching data from TempData...")  # 添加调试信息
        # threads=[]
        # for fileObj in TempData.objects.all():
        #     thread = threading.Thread(target=getOneTempDataJob, args=(fileObj, results))
        #     threads.append(thread)
        #     thread.start()
        # for thread in threads:
        #     thread.join()

        # 创建线程池，限制并发线程数量
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for fileObj in TempData.objects.all():
                future = executor.submit(getOneTempDataJob, fileObj, results)
                futures.append(future)

            # 等待所有任务完成
            for future in futures:
                future.result()
            
        # print(f"Final results: {len(results)} in total")  # 打印最终结果
        response_data = {
            'results': results,
            'count': len(results)
        }

        return JsonResponse(response_data, safe=False, json_dumps_params={'default': str})

    except Exception as e:
        # print(f"Error in getTempData: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
####
    


# @csrf_exempt
# def confirmTemp2esSingle(request):
#     es = get_elasticsearch_client()
    
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         doc_id = data['ID']

#         index_name = settings.INDEX_NAME
#         # for fileObj in TempData.objects.all():
#         #     jsonDict=json.loads(fileObj.jsonContent)
#         #     if jsonDict['ID'][0]==doc_id:
#         fileObj=TempData.objects.filter(jsonId=doc_id).first()
#         if fileObj:
#             # Check if the document already exists
#             response = es.exists(index=index_name, id=fileObj.fileName)
#             if response:
#                 return JsonResponse({'status':'error','error': f"File {fileObj.fileName} already exists"}, status=400)

#             # Recursively check and modify the 'Date' field if necessary
#             json_data = recursive_date_check(fileObj.jsonContent)

#             # Index the document if it does not exist
#             response = es.index(index=index_name, id=fileObj.fileName, document=json_data)
#             if response['result'] != 'created':
#                 return JsonResponse({'status':'error','error': f"Failed to upload {fileObj.fileName}"}, status=500)
            
#             fileObj.delete()
#             return JsonResponse({'message': 'File uploaded successfully'}, status=200)
#         return JsonResponse({'error': f"File {doc_id} not found in TempData"}, status=400)

# 处理单个 ID 的函数
lockConfirm=threading.Lock()
def process_single_confirm(doc_id, es, index_name, results):
    fileObj = TempData.objects.filter(jsonId=doc_id).first()
    result=""
    successState="failure"
    if fileObj:
        # Check if the document already exists
        response = es.exists(index=index_name, id=fileObj.fileName)
        if response:
            result=f"File {fileObj.fileName} already exists"
            successState="failure"
        else:
            # Recursively check and modify the 'Date' field if necessary
            json_data = recursive_date_check(fileObj.jsonContent)

            # Index the document if it does not exist
            response = es.index(index=index_name, id=fileObj.fileName, document=json_data)
            if response:
                if response['result'] != 'created':
                    result=f"Failed to upload {fileObj.fileName}"
                    successState="failure"
                else:
                    fileObj.delete()
                    result=f"File {fileObj.fileName} uploaded successfully"
                    successState="success"
            else:
                result=f"Elasticsearch error: {fileObj.fileName}"
                successState="failure"
    else:
        result=f"File {doc_id} not found in TempData"
        successState="failure"
    lockConfirm.acquire()
    results[successState].append(result)
    lockConfirm.release()

@csrf_exempt
def confirmTemp2es(request):
    es = get_elasticsearch_client()
    index_name = settings.INDEX_NAME
    results = {
        "success":[],
        "failure":[]
    }

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doc_ids = data.get('ID', [])

            # threads = []
            # for doc_id in doc_ids:
            #     thread = threading.Thread(target=process_single_confirm, args=(doc_id, es, index_name, results))
            #     threads.append(thread)
            #     thread.start()

            # # 等待所有线程完成
            # for thread in threads:
            #     thread.join()


            # 创建线程池，限制并发线程数量
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for doc_id in doc_ids:
                    future = executor.submit(process_single_confirm, doc_id, es, index_name, results)
                    futures.append(future)

                # 等待所有任务完成
                for future in futures:
                    future.result()

            return JsonResponse(results, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    cache.clear()
    return JsonResponse({'error': 'Invalid request method. Only POST is allowed'}, status=405)




# @csrf_exempt
# def deleteTempDataSingle(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             doc_id = data['ID']
#             fileObj=TempData.objects.filter(jsonId=doc_id).first()
#             if fileObj:
#                 fileObj.delete()
#                 return JsonResponse({'status': 'success', 'message': f'File {doc_id} deleted successfully'}, status=200)
#             # for fileObj in TempData.objects.all():
#             #     jsonDict=json.loads(fileObj.jsonContent)
#             #     if jsonDict['ID'][0]==doc_id:
#             #         fileObj.delete()
#             #         return JsonResponse({'status': 'success', 'message': f'File {doc_id} deleted successfully'}, status=200)
#             # print("File not found in TempData")
#             return JsonResponse({'status': 'error', 'message': f'File {doc_id} not found in TempData'}, status=400)
#         except Exception as e:
#             logger.error(f"Error deleting document: {str(e)}")
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# 处理单个 ID 的删除操作
lockDelete=threading.Lock() 
def process_single_delete(doc_id, results):
    fileObj = TempData.objects.filter(jsonId=doc_id).first()
    result=""
    successState="failure"
    if fileObj:
        try:
            fileObj.delete()
            result=f"File {fileObj.fileName} deleted successfully"
            successState="success"
        except Exception as e:
            result=f"Error deleting file {fileObj.fileName}: {str(e)}"
            successState="failure"
    else:
        result=f"File {doc_id} not found in TempData"
        successState="failure"
    lockDelete.acquire()
    results[successState].append(result)
    lockDelete.release()

@csrf_exempt
def deleteTempData(request):
    results = {
        "success": [],
        "failure": []
    }

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doc_ids = data.get('ID', [])

            # 创建线程池，限制并发线程数量
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for doc_id in doc_ids:
                    future = executor.submit(process_single_delete, doc_id, results)
                    futures.append(future)

                # 等待所有任务完成
                for future in futures:
                    future.result()

            return JsonResponse(results, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data in request body'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

########################################################################################









@csrf_exempt
def list_files(request):
    if request.method == 'GET':
        es = get_elasticsearch_client()
        index_name = settings.INDEX_NAME

        # Use a search query to get all documents
        response = es.search(index=index_name, body={"query": {"match_all": {}}}, size=7500)  # Adjust the size as needed
        filenames = [hit['_id'] for hit in response['hits']['hits']]

        filenames.sort(key=lambda x: int(x) if x.isdigit() else x)

        return JsonResponse({'files': filenames}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# <--------------------------------------------Individual Process------------------------------------------------------>

#  ------------------------------------------------SEROTYPE-------------------------------------------------------

def process_serotypes(start_date, end_date):
    start_time = time.time()
    es = get_elasticsearch_client()
    # Create the base query

    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": []
            }
        },
        "aggs": {
            "serotypes": {
                "terms": {
                    "field": "Serotype.keyword",  # Ensure this matches the field in your Elasticsearch index
                    "size": 7000  # Increase size to get all serotypes and then filter
                }
            }
        }
    }

    # Add date range filter only if start_date and end_date are provided
    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "Date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })

    res = es.search(index=settings.INDEX_NAME, body=query, size=0)  # Set size to 0 to return only aggregations

    serotype_data = []
    # serotype = [c.strip() for c in serotype.split(',')]
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']  # Initialize serotype within the loop
        if serotype != "NA":  # Exclude "NA" serotype
            serotype_count = serotype_bucket['doc_count']
            
            serotype_data.append({
                'name': serotype,
                'value': serotype_count
            })

    # Ensure only unique serotypes are counted correctly
    serotype_data = list({item['name']: item for item in serotype_data}.values())
    serotype_data = sorted(serotype_data, key=lambda x: x['value'], reverse=True)
    end_time = time.time()  # End time
    total_time = end_time - start_time
    # print(f"serotype process time: {total_time:.2f} seconds")
    return serotype_data

#  --------------------------------------------------MLST----------------------------------------------------------

def process_mlst(start_date, end_date, index_name=None):
    es = get_elasticsearch_client()
    # index_to_use = index_name if index_name else settings.INDEX_NAME
    # Create the base query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": []
            }
        },
        "aggs": {
            "mlst": {
                "terms": {
                    "field": "MLST.keyword",  # Ensure this matches the field in your Elasticsearch index
                    "size": 7000  # Increase size to get all serotypes and then filter
                }
            }
        }
    }

    # Add date range filter only if start_date and end_date are provided
    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "Date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })

    res = es.search(index=settings.INDEX_NAME , body=query, size=0)  # Set size to 0 to return only aggregations
    
    mlst_data = []
    for mlst_bucket in res['aggregations']['mlst']['buckets']:
        mlst = mlst_bucket['key'] 
        
        if mlst != "NA": 
            mlst_count = mlst_bucket['doc_count']
            
            mlst_data.append({
                'name': mlst,
                'value': mlst_count
            })
  
    # Ensure only unique serotypes are counted correctly
    mlst_data = list({item['name']: item for item in mlst_data}.values())
    
    # Sort serotype data by count in descending order and take the top 10
    mlst_data = sorted(mlst_data, key=lambda x: x['value'], reverse=True)
    # print(f"Returning {len(mlst_data)} MLST")
    return mlst_data

#  --------------------------------------------------Source----------------------------------------------------------


def process_source(start_date, end_date):
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }


    query["aggs"] = {
        
    "pmcid": {
        "terms": {"field": "ID.keyword", "size": 7000},  
        "aggs": {
                "serotype": {
                    "terms": {"field": "Serotype.keyword", "size": 7000},  
                    "aggs": {
                        "source": {
                            "terms": {"field": "Source.keyword", "size": 7000},  
                            }
                        }
                    }
                }
             }
    }
    res = es.search(index=settings.INDEX_NAME, body=query, size=0)

    source_data = []

    for pmc_bucket in res['aggregations']['pmcid']['buckets']:
        for sero_bucket in pmc_bucket['serotype']['buckets']:
            serotype = sero_bucket['key']
            
            if serotype != "NA" : #and "Salmonella" in serotype:
                        
                for source_bucket in sero_bucket['source']['buckets']:
                    source = source_bucket['key']
                   
                    if source != "NA": 
                        source_count = source_bucket['doc_count']
                    
                        source_data.append({
                            'name': source,
                            'value': source_count
                        })
    aggregated_data = {}
    for item in source_data:
        name = item['name']
        value = item['value']
        if name in aggregated_data:
            aggregated_data[name]['value'] += value  # Increment the count
        else:
            aggregated_data[name] = item


    source_data = list(aggregated_data.values())

    # source_data = list({item['name']: item for item in source_data}.values())
   

    source_data = sorted(source_data, key=lambda x: x['value'], reverse=True)

    return source_data



# <--------------------------------------------COUNTRY RELATED------------------------------------------------------>

def country_serotype(start_date, end_date):
    es = get_elasticsearch_client()
    
    # Create the base query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": []
            }
        },
        "aggs": {
            "serotypes": {
                "terms": {
                    "field": "Serotype.keyword",
                    "size": 7000
                },
                "aggs": {
                    "associated_countries": {
                        "terms": {
                            "field": "Country.keyword",
                            "size": 7000
                        }
                    }
                }
            }
        }
    }

    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "Date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })

    res = es.search(index=settings.INDEX_NAME, body=query, size=0)

    serotype_data = []
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']
        if serotype != "NA":
            serotype_count = serotype_bucket['doc_count']
            countries = [
                {
                    'country': country_bucket['key'],
                }
                for country_bucket in serotype_bucket['associated_countries']['buckets']
            ]
            serotype_data.append({
                'name': serotype,
                'value': serotype_count,
                'countries': countries
            })

    country_sero = sorted(serotype_data, key=lambda x: x['value'], reverse=True)[:10]
    return country_sero



def fetch_country_counts(start_date, end_date):
    es = get_elasticsearch_client()
    
    # Create the base query
    query = {"query": {"match_all": {}}}

    # Modify the query if start_date and end_date are provided
    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }

    res = es.search(index=settings.INDEX_NAME, body=query, size=10000)
    country_counts = {}
    
    delimiter_pattern = re.compile(r'(?<=\s)(?:and|,|;)(?=\s)|^and\s|,|;$')

    for hit in res['hits']['hits']:

        c = (hit['_source'].get('Country'))[0]
        if c:

                if c in country_counts:
                    country_counts[c] += 1
                else:
                    country_counts[c] = 1


    top_countries = dict(Counter(country_counts).most_common(10))

    return top_countries

def process_sero_MLST(start_date, end_date):
    start_time = time.time()
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }

    # Add aggregation for serotypes and MLST
    query["aggs"] = {
        "serotypes": {
            "terms": {"field": "Serotype.keyword", "size": 7000},  # Top 10 Serotypes
            "aggs": {
                "top_mlst": {
                    "terms": {"field": "MLST.keyword", "size": 7000}  # Top 3 MLST per serotype
                }    
            }
        }
    }

    res = es.search(index=settings.INDEX_NAME, body=query, size=0)
    # serotype = [c.strip() for c in serotype.split(',')]
    serotype_MLST_data = []
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']

        if serotype != "NA":
            serotype_count = serotype_bucket['doc_count']  # Count of documents for this serotype
            mlst_buckets = serotype_bucket['top_mlst']['buckets']
            # mlst_data = [{'mlst': mlst['key'], 'count': mlst['doc_count']} for mlst in mlst_buckets]
            mlst_data=[mlst['key'] for mlst in mlst_buckets]
            serotype_MLST_data.append({
                'serotype': serotype,
                'count': serotype_count,  # Include the count in the result
                'mlst': mlst_data
            })
    end_time = time.time()  # End time
    total_time = end_time - start_time
    # print(f"middle query: {total_time:.2f} seconds")
    return serotype_MLST_data

logger = logging.getLogger(__name__)

   
def geo_dis(start_date, end_date, serotype,source, serotype_condition, source_condition):
    es = get_elasticsearch_client()
    
    serotype = serotype.split(',') if serotype else []
    source = source.split(',') if source else []
    query = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        }
    }

    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "Date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })
    
 
    if serotype:
         
        serotype_conditions = [{"match": {"Serotype": {"query": s, "operator": "and"}}} for s in serotype]
        if serotype_condition == 'must':
            query["query"]["bool"]["must"].extend(serotype_conditions)
        else:
            query["query"]["bool"]["should"] = query["query"]["bool"].get("should", []) + serotype_conditions
            query["query"]["bool"]["minimum_should_match"] = 1

    if source:
        source_conditions = [{"match": {"Source": {"query": s, "operator": "and"}}} for s in source]
        if source_condition == 'must':
            query["query"]["bool"]["must"].extend(source_conditions)
        else:
            query["query"]["bool"]["should"] = query["query"]["bool"].get("should", []) + source_conditions
            query["query"]["bool"]["minimum_should_match"] = 1



    res = es.search(index=settings.INDEX_NAME, body=query, size=10000)
    country_counts = {}
    


    for hit in res['hits']['hits']:
        c = (hit['_source'].get('Country'))[0]
        if c:
                if c in country_counts:
                    country_counts[c] += 1
                else:
                    country_counts[c] = 1

    countries = dict(Counter(country_counts))
    return countries

def process_country_source(start_date, end_date):
    start_time = time.time()
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }

  
    query["aggs"] = {
        "serotypes": {
            "terms": {"field": "Serotype.keyword", "size": 7000},  
            "aggs": {
                "date": {
                    "terms": {"field": "Date", "size": 7000},  # All pub_years associated with the serotype
                    "aggs": {
                        "top_countries": {
                            "terms": {"field": "Country.keyword", "size": 7000},  # Top countries per serotype per pub_year
                            "aggs": {
                                "top_sources": {
                                    "terms": {"field": "Source.keyword", "size": 7000}  # Top sources per serotype per pub_year
                                }
                             
                    }
                }
            }
        }
    }
        }
    }

    res = es.search(index=settings.INDEX_NAME, body=query, size=1000)
    serotype_country_source_data = []
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']

        if serotype != "NA":
            # Process each publication year bucket within the serotype
            for pub_year_bucket in serotype_bucket['date']['buckets']:
                date = datetime.utcfromtimestamp(pub_year_bucket['key'] / 1000).strftime('%Y-%m-%d')

                # Create a temporary dictionary to store country and source counts
                temp_data = {}

                # Process each country bucket within the publication year
                for country_bucket in pub_year_bucket['top_countries']['buckets']:
                    country = country_bucket['key']
                    country_count = country_bucket['doc_count']
                    
                    if country not in temp_data:
                        temp_data[country] = {'sources': {}, 'count': country_count}
                    else:
                        temp_data[country]['count'] += country_count

                    # Process each source bucket within the country bucket
                    for source_bucket in country_bucket['top_sources']['buckets']:
                        source = source_bucket['key']
                        source_count = source_bucket['doc_count']

                        # Only add sources to the corresponding country
                        if source_count <= country_count:
                            if source not in temp_data[country]['sources']:
                                temp_data[country]['sources'][source] = source_count
                            else:
                                temp_data[country]['sources'][source] += source_count

                # Combine the aggregated data for countries and sources
                for country, data in temp_data.items():
                    for source, count in data['sources'].items():
                        serotype_country_source_data.append({
                            'serotype': serotype,
                            'count': count,  # Use the aggregated count for the country and source
                            'country': country,
                            'source': source,
                            'pub_years': date
                        })
    end_time = time.time()  # End time
    total_time = end_time - start_time
    # print(f"serotype_country_source_data: {total_time:.2f} seconds")
    return serotype_country_source_data

def process_mlst_table(start_date, end_date):
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }

  
    query["aggs"] = {
        "mlst": {
            "terms": {"field": "MLST.keyword", "size": 7000},  
            "aggs": {
                "pub_years": {
                    "terms": {"field": "Date", "size": 7000},  # All pub_years associated with the serotype
                    "aggs": {
                        "top_countries": {
                            "terms": {"field": "Country.keyword", "size":7000},  # Top countries per serotype per pub_year
                            "aggs": {
                                "top_sources": {
                                    "terms": {"field": "Source.keyword", "size": 7000}  # Top sources per serotype per pub_year
                                }
                             
                    }
                }
            }
        }
    }
        }
    }

    res = es.search(index=settings.INDEX_NAME, body=query, size=7000)
    mlst_table_data = []
    for mlst_bucket in res['aggregations']['mlst']['buckets']:
        mlst = mlst_bucket['key']
        # # print(f"Processing mlst: {mlst}")

        if mlst != "NA":
            # Process each publication year bucket within the serotype
            for pub_year_bucket in mlst_bucket['pub_years']['buckets']:
                pub_year = datetime.utcfromtimestamp(pub_year_bucket['key'] / 1000).strftime('%Y-%m-%d')
                # # print(f"  Processing publication year: {pub_year}")

                # Create a temporary dictionary to store country and source counts
                temp_data = {}

                # Process each country bucket within the publication year
                for country_bucket in pub_year_bucket['top_countries']['buckets']:
                    country = country_bucket['key']
                    country_count = country_bucket['doc_count']
                    # # print(f"    Processing country: {country} with count: {country_count}")
                    
                    if country not in temp_data:
                        temp_data[country] = {'sources': {}, 'count': country_count}
                    else:
                        temp_data[country]['count'] += country_count

                    # Process each source bucket within the country bucket
                    for source_bucket in country_bucket['top_sources']['buckets']:
                        source = source_bucket['key']
                        source_count = source_bucket['doc_count']
                        # # print(f"      Processing source: {source} with count: {source_count}")

                        # Only add sources to the corresponding country
                        if source_count <= country_count:
                            if source not in temp_data[country]['sources']:
                                temp_data[country]['sources'][source] = source_count
                            else:
                                temp_data[country]['sources'][source] += source_count

                # Combine the aggregated data for countries and sources
                for country, data in temp_data.items():
                    # # print(f"Country: {country}, Data: {data}")
                    for source, count in data['sources'].items():
                        # # print(f"  Source: {source}, Count: {count}")
                        mlst_table_data.append({
                            'mlst ': mlst,
                            'count': count,  # Use the aggregated count for the country and source
                            'country': country,
                            'source': source,
                            'pub_years': pub_year
                        })
    # print(f"Returning {len(mlst_table_data)} mlst_table_data records")
    return mlst_table_data

# ---------------------------------------------------------Serovar Monitoring--------------------------------------------

def process_ID_sero(start_date, end_date):
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            },  # Adjust size as needed
        }

    res = es.search(index=settings.INDEX_NAME, body=query, size=7000)  # Adjust size as needed
    records_s = []
    
    for hit in res['hits']['hits']:
        record = hit['_source']
        records_s.append({
            "ID": record.get("ID"),
            "Date": record.get("Date"),
            "Serotype": record.get("Serotype")
        })
   
    return records_s

# ---------------------------------------------------------MLST Monitoring--------------------------------------------

def process_ID_MLST(start_date, end_date):
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    query = {
            "query": {
                "range": {
                    "Date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            },  # Adjust size as needed
        }

    res = es.search(index=settings.INDEX_NAME, body=query, size=7000)  # Adjust size as needed
    records_m = []
    
    for hit in res['hits']['hits']:
        record = hit['_source']
        records_m.append({
            "ID": record.get("ID"),
            "Date": record.get("Date"),
            "MLST": record.get("MLST")
        })
   
    return records_m

# <--------------------------------------------for ASSAY INFORMATION SET------------------------------------------------------>
#我写的方便使用的查询函数
def query_fetch_all_within_one_date_range(start_date, end_date, date_format='yyyy'):
    return {
        "query":{
            "bool":{
                "should":[
                    {
                        "range":{
                            "isolates_with_linking.isolate_date":{
                                "gte": start_date,
                                "lte": end_date,
                                "format": date_format
                            }
                        }
                    },
                    {
                        "range":{
                            "no_isolates_only_assayinformation.isolate_date":{
                                "gte": start_date,
                                "lte": end_date,
                                "format": date_format
                            }
                        }
                    }
                ]
            }
        }
    }
#我写的方便使用的查询函数
def query_fetch_all_within_date_range(start_date, end_date):
    date_format = "yyyy-MM-dd || yyyy-MM || yyyy"
    return {
        "query":{
            "bool":{
                "should":[
                    {
                        "range":{
                            "isolates_with_linking.isolate_date":{
                                "gte": start_date,
                                "lte": end_date,
                                "format": date_format
                            }
                        }
                    },
                    {
                        "range":{
                            "no_isolates_only_assayinformation.isolate_date":{
                                "gte": start_date,
                                "lte": end_date,
                                "format": date_format
                            }
                        }
                    }
                ]
            }
        }
    }



def process_isolate_country_source_assay(index_name):
    start_time = time.time()
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    query["aggs"] = {
        "serotypes": {
            "terms": {"field": "Serotype.keyword", "size": 348},  # Limiting size to 348 as requested
            "aggs": {
                "date": {
                    "terms": {"field": "Date", "size": 348},  # Limiting date aggregation to 348
                    "aggs": {
                        "top_isolate_countries": {
                            "terms": {"field": "isolate_country.keyword", "size": 348},  # Using isolate_country instead of Country
                            "aggs": {
                                "top_isolate_sources": {
                                    "terms": {"field": "isolate_source.keyword", "size": 348}  # Using isolate_source instead of Source
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    res = es.search(index=settings.INDEX_NAME, body=query, size=1000)
    serotype_isolate_country_source_data = []
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']

        if serotype != "NA":
            # Process each publication year bucket within the serotype
            for pub_year_bucket in serotype_bucket['date']['buckets']:
                date = datetime.utcfromtimestamp(pub_year_bucket['key'] / 1000).strftime('%Y-%m-%d')

                # Create a temporary dictionary to store country and source counts
                temp_data = {}

                # Process each isolate_country bucket within the publication year
                for isolate_country_bucket in pub_year_bucket['top_isolate_countries']['buckets']:
                    isolate_country = isolate_country_bucket['key']
                    country_count = isolate_country_bucket['doc_count']
                    
                    if isolate_country not in temp_data:
                        temp_data[isolate_country] = {'sources': {}, 'count': country_count}
                    else:
                        temp_data[isolate_country]['count'] += country_count

                    # Process each isolate_source bucket within the isolate_country bucket
                    for isolate_source_bucket in isolate_country_bucket['top_isolate_sources']['buckets']:
                        isolate_source = isolate_source_bucket['key']
                        source_count = isolate_source_bucket['doc_count']

                        # Only add sources to the corresponding isolate_country
                        if source_count <= country_count:
                            if isolate_source not in temp_data[isolate_country]['sources']:
                                temp_data[isolate_country]['sources'][isolate_source] = source_count
                            else:
                                temp_data[isolate_country]['sources'][isolate_source] += source_count

                # Combine the aggregated data for isolate_countries and sources
                for isolate_country, data in temp_data.items():
                    for isolate_source, count in data['sources'].items():
                        serotype_isolate_country_source_data.append({
                            'serotype': serotype,
                            'count': count,  # Use the aggregated count for the isolate_country and isolate_source
                            'isolate_country': isolate_country,
                            'isolate_source': isolate_source,
                            'pub_years': date
                        })

    end_time = time.time()  # End time
    total_time = end_time - start_time
    # print(f"serotype_isolate_country_source_data: {total_time:.2f} seconds")
    return serotype_isolate_country_source_data

#word cloud
#laiyi edited huhan finished
def process_serotypes_assay(start_date, end_date, index_name):
    es = get_elasticsearch_client()
    
    # 使用正确的查询
    query = query_fetch_all_within_date_range(start_date, end_date)
    
    # 直接搜索文档
    res = es.search(index=index_name, body=query, size=348)
    
    # 手动处理结果
    serotype_counts = {}
    
    for hit in res['hits']['hits']:
        source = hit['_source']
        
        # 处理isolates_with_linking中的数据
        if 'isolates_with_linking' in source and source['isolates_with_linking']:
            for isolate in source['isolates_with_linking']:
                for serotype_or_Serotype in ['serotype', 'Serotype']:
                    if serotype_or_Serotype in isolate and isolate[serotype_or_Serotype]:
                        serotype = isolate[serotype_or_Serotype]
                        if isinstance(serotype, list):
                            for s in serotype:
                                if s != "NA":
                                    serotype_counts[s] = serotype_counts.get(s, 0) + 1
                        elif serotype != "NA":
                            serotype_counts[serotype] = serotype_counts.get(serotype, 0) + 1
        
        # 处理no_isolates_only_assayinformation中的数据
        if 'no_isolates_only_assayinformation' in source and source['no_isolates_only_assayinformation']:
            isolate = source['no_isolates_only_assayinformation']
            for serotype_or_Serotype in ['serotype', 'Serotype']:
                if serotype_or_Serotype in isolate and isolate[serotype_or_Serotype]:
                    serotype = isolate[serotype_or_Serotype]
                    if isinstance(serotype, list):
                        for s in serotype:
                            if s != "NA":
                                serotype_counts[s] = serotype_counts.get(s, 0) + 1
                    elif serotype != "NA":
                        serotype_counts[serotype] = serotype_counts.get(serotype, 0) + 1
    
    # 转换为所需的输出格式
    serotype_data = [{'name': serotype, 'value': count} for serotype, count in serotype_counts.items()]
    
    # 按计数排序
    serotype_data = sorted(serotype_data, key=lambda x: x['value'], reverse=True)
    
    return serotype_data

#word cloud
#laiyi edited huhan finished
def process_mlst_assay(start_date, end_date, index_name):
    es = get_elasticsearch_client()
    
    # 使用正确的查询
    query = query_fetch_all_within_date_range(start_date, end_date)
    
    # 直接搜索文档
    res = es.search(index=index_name, body=query, size=348)
    
    # 手动处理结果
    mlst_counts = {}
    
    for hit in res['hits']['hits']:
        source = hit['_source']
        
        # 处理isolates_with_linking中的数据
        if 'isolates_with_linking' in source and source['isolates_with_linking']:
            for isolate in source['isolates_with_linking']:
                for mlst_or_MLST in ['mlst', 'MLST']:
                    if mlst_or_MLST in isolate and isolate[mlst_or_MLST]:
                        mlst = isolate[mlst_or_MLST]
                        if isinstance(mlst, list):
                            for m in mlst:
                                if m != "NA":
                                    mlst_counts[m] = mlst_counts.get(m, 0) + 1
                        elif mlst != "NA":
                            mlst_counts[mlst] = mlst_counts.get(mlst, 0) + 1
        
        # 处理no_isolates_only_assayinformation中的数据
        if 'no_isolates_only_assayinformation' in source and source['no_isolates_only_assayinformation']:
            isolate = source['no_isolates_only_assayinformation']
            for mlst_or_MLST in ['mlst', 'MLST']:
                if mlst_or_MLST in isolate and isolate[mlst_or_MLST]:
                    mlst = isolate[mlst_or_MLST]
                    if isinstance(mlst, list):
                        for m in mlst:
                            if m != "NA":
                                mlst_counts[m] = mlst_counts.get(m, 0) + 1
                    elif mlst != "NA":
                        mlst_counts[mlst] = mlst_counts.get(mlst, 0) + 1
    
    # 转换为所需的输出格式
    mlst_data = [{'name': mlst, 'value': count} for mlst, count in mlst_counts.items()]
    
    # 按计数排序
    mlst_data = sorted(mlst_data, key=lambda x: x['value'], reverse=True)
    
    return mlst_data


def process_source_assay(start_date, end_date,index_name):
    start_time = time.time()
    es = get_elasticsearch_client()

    # Create the base query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": []
            }
        },
        "aggs": {
            "isolate_source": {
                "terms": {
                    "field": "isolate_source.keyword",  # Aggregate by the source
                    "size": 348  # Adjust size according to the number of sources
                }
            }
        }
    }

    res = es.search(index=index_name, body=query, size=0)  # Set size to 0 to return only aggregations
      # Optional: # print the result to debug

    source_data = []
    
    # Iterate over the aggregation results and populate source_data
    for source_bucket in res['aggregations']['isolate_source']['buckets']:
        source = source_bucket['key']
        if source != "NA":  # Exclude "NA" source
            source_count = source_bucket['doc_count']
            source_data.append({
                'name': source,
                'value': source_count
            })

    # Ensure only unique sources are counted correctly
    source_data = list({item['name']: item for item in source_data}.values())
    
    # Sort source_data by the 'value' in descending order
    source_data = sorted(source_data, key=lambda x: x['value'], reverse=True)
    
    end_time = time.time()  # End time
    total_time = end_time - start_time
    # # print("aaaa",source_data)
    
    return source_data

#finished
def geo_dis_assay(start_date, end_date, serotype, source, serotype_condition, source_condition, index_name):
    es = get_elasticsearch_client()

    serotype = serotype.split(',') if serotype else []
    source = source.split(',') if source else []
    # query = {
    #     "query": {
    #         "bool": {
    #             "must": [],
    #             "should":query_fetch_all_within_date_range(start_date, end_date)["query"]["bool"]["should"],
    #             "filter": []
    #         }
    #     }
    # }
    query=query_fetch_all_within_date_range(start_date, end_date)
    query["query"]["bool"]["filter"] = []
    query["query"]["bool"]["must"]=[]

    parent_fields=["no_isolates_only_assayinformation","isolates_with_linking"]
    if serotype:
        serotype_conditions = []
        for parent_field in parent_fields:
            serotype_conditions+=[{"match": {f"{parent_fields}.serotype": {"query": s, "operator": "and"}}} for s in serotype]
            serotype_conditions+=[{"match": {f"{parent_fields}.Serotype": {"query": s, "operator": "and"}}} for s in serotype]
        if serotype_condition == 'must':
            query["query"]["bool"]["must"].extend(serotype_conditions)
        else:
            query["query"]["bool"]["should"] = query["query"]["bool"].get("should", []) + serotype_conditions
            query["query"]["bool"]["minimum_should_match"] = 1

    if source:
        source_conditions = []
        for parent_field in parent_fields:
            source_conditions+=[{"match": {f"{parent_fields}.isolate_source": {"query": s, "operator": "and"}}} for s in source]
        if source_condition == 'must':
            query["query"]["bool"]["must"].extend(source_conditions)
        else:
            query["query"]["bool"]["should"] = query["query"]["bool"].get("should", []) + source_conditions
            query["query"]["bool"]["minimum_should_match"] = 1

    # index_a = 'assay_data'
    # print("index_a:",index_name)
    res = es.search(index=index_name, body=query, size=348)
    # print(len(res['hits']['hits']))
    country_counts = {}

    for hit in res['hits']['hits']:
        country_name=None
        for isolate in hit['_source']['isolates_with_linking']:
            country_name=isolate['isolate_country']
        if hit['_source']['no_isolates_only_assayinformation']:
            country_name=hit['_source']['no_isolates_only_assayinformation']['isolate_country']
        if country_name:
            if isinstance(country_name, str):
                country_name = [country_name]
            for c in country_name:
                c1=c
                if ':' in c:
                    c1=c.split(':')[0]
                if c1 in country_counts:
                    country_counts[c1] += 1
                else:
                    country_counts[c1] = 1

    # for hit in res['hits']['hits']:
    #     country_name = hit['_source'].get('countryname')
    #     if country_name==None:
    #         country_name=hit['_source'].get('country')
    #     # # print(country_name)
    #     # Log the country_name to see what it's retrieving
        

    #     if country_name:
    #         if isinstance(country_name, str):
    #             country_name = [country_name]
    #         for c in country_name:
    #             if c in country_counts:
    #                 country_counts[c] += 1
    #             else:
    #                 country_counts[c] = 1

    cleaned_country_counts = {}

    for country, count in country_counts.items():
        # Clean and process the country names
        if country == "Viet Nam":
            country = "Vietnam"

        
        cleaned_country = re.sub(r"\s*\(.*?\)\s*", "", country).strip()
        # # print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",cleaned_country)
        if cleaned_country == "United States of America":
           cleaned_country  = "United States"
        
        # Handle "and" in country names
        if "and" in cleaned_country:
            parts = cleaned_country.split(" and ")

            for part in parts:
                part = part.strip()
                if part in cleaned_country_counts:
                    cleaned_country_counts[part] += count
                else:
                    cleaned_country_counts[part] = count
        else:
            if cleaned_country in cleaned_country_counts:
                cleaned_country_counts[cleaned_country] += count
            else:
                cleaned_country_counts[cleaned_country] = count
        
    
    countries = dict(Counter(cleaned_country_counts))
    # # print(countries)
    return countries

#laiyi edited frank finished
def process_country_source_a(start_date, end_date, index_name):
    print("process country source data: ",index_name)
    es = get_elasticsearch_client()
    
    # 使用正确的查询构建方式
    query = query_fetch_all_within_date_range(start_date, end_date)
    
    # 执行查询
    res = es.search(index=index_name, body=query, size=348)
    
    # 数据处理部分
    serotype_country_source_data = []
    
    for hit in res['hits']['hits']:
        record = hit['_source']
        
        # 处理isolates_with_linking中的数据
        if "isolates_with_linking" in record and record["isolates_with_linking"]:
            for isolate in record["isolates_with_linking"]:
                for serotype_or_Serotype in ["serotype","Serotype"]:
                    if serotype_or_Serotype in isolate and isolate[serotype_or_Serotype] and isolate[serotype_or_Serotype] != "NA":
                        serotype = isolate[serotype_or_Serotype]
                        date = isolate.get("isolate_date", ["Unknown"])[0] if isinstance(isolate.get("isolate_date", []), list) else isolate.get("isolate_date", "Unknown")
                        country = isolate.get("isolate_country", "Unknown")
                        source = isolate.get("isolate_source", "Unknown")
                        
                        # 创建记录
                        entry = {
                            'serotype': serotype,
                            'count': 1,  # 默认计数为1
                            'country': country,
                            'source': source,
                            'pub_years': date
                        }
                        serotype_country_source_data.append(entry)
        
        # 处理no_isolates_only_assayinformation中的数据
        if "no_isolates_only_assayinformation" in record and record["no_isolates_only_assayinformation"]:
            isolate = record["no_isolates_only_assayinformation"]
            for serotype_or_Serotype in ["serotype","Serotype"]:
                if serotype_or_Serotype in isolate and isolate[serotype_or_Serotype] and isolate[serotype_or_Serotype] != "NA":
                    serotype = isolate[serotype_or_Serotype]
                    date = isolate.get("isolate_date", ["Unknown"])[0] if isinstance(isolate.get("isolate_date", []), list) else isolate.get("isolate_date", "Unknown")
                    country = isolate.get("isolate_country", "Unknown")
                    source = isolate.get("isolate_source", "Unknown")
                    
                    # 创建记录
                    entry = {
                        'serotype': serotype,
                        'count': 1,  # 默认计数为1
                        'country': country,
                        'source': source,
                        'pub_years': date
                    }
                    serotype_country_source_data.append(entry)
    
    # 聚合相同serotype、country、source和pub_years的记录
    aggregated_data = {}
    for entry in serotype_country_source_data:
        key = f"{entry['serotype']}-{entry['country']}-{entry['source']}-{entry['pub_years']}"
        if key in aggregated_data:
            aggregated_data[key]['count'] += entry['count']
        else:
            aggregated_data[key] = entry.copy()
    
    return list(aggregated_data.values())

#laiyi edited huhan finished
def process_mlst_table_a(start_date, end_date, index_name):
    es = get_elasticsearch_client()
    
    # 使用正确的查询构建方式
    query = query_fetch_all_within_date_range(start_date, end_date)
    
    # 执行查询
    res = es.search(index=index_name, body=query, size=348)
    
    # 数据处理部分
    mlst_table_data = []
    
    for hit in res['hits']['hits']:
        record = hit['_source']
        
        # 处理isolates_with_linking中的数据
        if "isolates_with_linking" in record and record["isolates_with_linking"]:
            for isolate in record["isolates_with_linking"]:
                for mlst_or_MLST in ["mlst","MLST"]:
                    if mlst_or_MLST in isolate and isolate[mlst_or_MLST] and isolate[mlst_or_MLST] != "NA":
                        # 确保mlst不是空数组或空字符串
                        mlst = isolate[mlst_or_MLST]
                        if isinstance(mlst, list) and len(mlst) > 0:
                            mlst = mlst[0]  # 取第一个元素
                        elif not mlst:  # 如果是空的
                            continue
                            
                        date = isolate.get("isolate_date", ["Unknown"])[0] if isinstance(isolate.get("isolate_date", []), list) else isolate.get("isolate_date", "Unknown")
                        country = isolate.get("isolate_country", "Unknown")
                        source = isolate.get("isolate_source", "Unknown")
                        serotype=isolate.get("serotype","Unknown")
                        serotype=isolate.get("Serotype",serotype)
                        # 创建记录，注意这里字段名是'mlst'，不是'mlst '（没有空格）
                        entry = {
                            'mlst': mlst,
                            'count': 1,  # 默认计数为1
                            'country': country,
                            'source': source,
                            'pub_years': date,
                            "serotype": serotype
                        }
                        mlst_table_data.append(entry)
        
        # 处理no_isolates_only_assayinformation中的数据
        if "no_isolates_only_assayinformation" in record and record["no_isolates_only_assayinformation"]:
            isolate = record["no_isolates_only_assayinformation"]
            for mlst_or_MLST in ["mlst","MLST"]:
                if mlst_or_MLST in isolate and isolate[mlst_or_MLST] and isolate[mlst_or_MLST] != "NA":
                    # 确保mlst不是空数组或空字符串
                    mlst = isolate[mlst_or_MLST]
                    if isinstance(mlst, list) and len(mlst) > 0:
                        mlst = mlst[0]  # 取第一个元素
                    elif not mlst:  # 如果是空的
                        continue
                        
                    date = isolate.get("isolate_date", ["Unknown"])[0] if isinstance(isolate.get("isolate_date", []), list) else isolate.get("isolate_date", "Unknown")
                    country = isolate.get("isolate_country", "Unknown")
                    source = isolate.get("isolate_source", "Unknown")
                    serotype=isolate.get("serotype","Unknown")
                    serotype=isolate.get("Serotype",serotype)
                    entry = {
                        'mlst': mlst,
                        'count': 1,  # 默认计数为1
                        'country': country,
                        'source': source,
                        'pub_years': date,
                        'serotype':serotype
                    }
                    mlst_table_data.append(entry)
        
    # 聚合相同mlst、country、source和pub_years的记录
    aggregated_data = {}

    for entry in mlst_table_data:
        # 确保mlst不是空的
        if not entry['mlst']:
            continue
            
        key = f"{entry['mlst']}-{entry['country']}-{entry['source']}-{entry['pub_years']}"
        if key in aggregated_data:
            aggregated_data[key]['count'] += entry['count']
        else:
            aggregated_data[key] = entry.copy()
    
    # 返回前检查数据
    result = list(aggregated_data.values())
    print(f"返回的MLST表数据数量: {len(result)}")
    if result:
        print(f"样例MLST数据: {result[0]}")
    
    return result



#finished
def process_ID_MLST_a(start_date, end_date,index_name):
    es = get_elasticsearch_client()
    query=query_fetch_all_within_date_range(start_date, end_date)
    res = es.search(index=index_name, body=query, size=348)  # Adjust size as needed

    records_m = []
    

    # for hit in res['hits']['hits']:
    #     record = hit['_source']
    #     pmcid = record.get("mlst")
    #     if pmcid:
    #         total_pmcid_count = total_pmcid_count + 1
    #     records_m.append({
    #         "ID": record.get("pmcid"),
    #         "Date": record.get("isolate_date"),
    #         "MLST": record.get("mlst")
    #     })
    for hit in res['hits']['hits']:
        record=hit['_source']
        add_records_s={
            "ID":record["pmcid"],
            "Date":["NaT"],
            "MLST":["Unknown MLST"]
        }
        if record["isolates_with_linking"]:
            for isolate in record["isolates_with_linking"]:
                if "isolate_date" in isolate and isolate["isolate_date"][0]!=1850 and isolate["isolate_date"][0]!=1900:
                    add_records_s["Date"]=isolate["isolate_date"]
                if "mlst" in isolate:
                    add_records_s["MLST"]=isolate["mlst"]
                elif "MLST" in isolate:
                    add_records_s["MLST"]=isolate["MLST"]
        if record["no_isolates_only_assayinformation"]:
            isolate=record["no_isolates_only_assayinformation"]
            if "isolate_date" in isolate and isolate["isolate_date"][0]!=1850 and isolate["isolate_date"][0]!=1900:
                add_records_s["Date"]=isolate["isolate_date"]
            if "mlst" in isolate:
                add_records_s["MLST"]=isolate["mlst"]
            elif "MLST" in isolate:
                add_records_s["MLST"]=isolate["MLST"]
        records_m.append(add_records_s)
    print(len(records_m))

    
    return records_m

#finished
def process_ID_sero_a(start_date, end_date, index_name):
    es = get_elasticsearch_client()
    print("data range:",start_date, end_date)
    query=query_fetch_all_within_date_range(start_date, end_date)

    res = es.search(index=index_name, body=query, size=348)  # Adjust size as needed
    records_s = []
    print("response length:",len(res['hits']['hits']))

    for hit in res['hits']['hits']:
        record=hit['_source']
        add_records_s={
            "ID":record["pmcid"],
            "Date":["NaT"],
            "Serotype":["Unknown Serotype"]
        }
        if record["isolates_with_linking"]:
            for isolate in record["isolates_with_linking"]:
                if "isolate_date" in isolate and isolate["isolate_date"][0]!=1850 and isolate["isolate_date"][0]!=1900:
                    add_records_s["Date"]=isolate["isolate_date"]
                if "serotype" in isolate:
                    add_records_s["Serotype"]=isolate["serotype"]
                elif "Serotype" in isolate:
                    add_records_s["Serotype"]=isolate["Serotype"]
        if record["no_isolates_only_assayinformation"]:
            isolate=record["no_isolates_only_assayinformation"]
            if "isolate_date" in isolate and isolate["isolate_date"][0]!=1850 and isolate["isolate_date"][0]!=1900:
                add_records_s["Date"]=isolate["isolate_date"]
            if "serotype" in isolate:
                add_records_s["Serotype"]=isolate["serotype"]
            elif "Serotype" in isolate:
                add_records_s["Serotype"]=isolate["Serotype"]
        records_s.append(add_records_s)
    print(len(records_s))
    
    return records_s



































# from django.http import JsonResponse
# # from .es_call import esearch (assay information)
# from .es_call import esearch_local
# from elasticsearch import Elasticsearch
# from django.conf import settings
# import re
# from collections import Counter
# from django.views.decorators.csrf import csrf_exempt
# import json
# import logging
# from datetime import datetime
# from elasticsearch_dsl.utils import AttrList


# <--------------------------------------------Assay information------------------------------------------------------>

# def search_index(request):
    # Collect query parameters
    params = {
        'title': request.GET.get('title', ''),
        'pmcid': request.GET.get('pmcid', ''),
        'abstract': request.GET.get('abstract', ''),
        'keyword': request.GET.get('keyword', ''),
        'source': request.GET.get('source', ''),
        'pub_country': request.GET.get('pub_country', ''),
        'pub_year': request.GET.get('pub_year', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'doi': request.GET.get('doi', ''),
        'country': request.GET.get('country', ''),
        'serotype': request.GET.get('serotype', ''),
        'date': request.GET.get('date',''),
        'serotype_condition': request.GET.get('serotype_condition', ''),
        'source_condition': request.GET.get('source_condition', ''),
        'required_data': request.GET.get('required_data', '')
    }
    required_data = params['required_data'].split(',') if params['required_data'] else []
    
    search_params = {k: v for k, v in params.items() if v}
    # print (search_params)
    results = esearch(**search_params)
   
    response_data = {
        'results': results,
        'count': len(results)
    }


    
    # print ("here:",params['required_data'])
    # Conditionally call functions based on required_data
    if 'serotypes' in params['required_data']:
        serotype_data = process_serotypes(params['start_date'], params['end_date'])
        response_data['serotypes'] = serotype_data

    if 'mlst' in params['required_data']:
        mlst_data = process_mlst(params['start_date'], params['end_date'])
        response_data['mlst'] = mlst_data

    if 'sourcetype' in params['required_data']:
        source_data = process_source(params['start_date'], params['end_date'])
        response_data['sourcetype'] = source_data

    if 'country_counts' in params['required_data']:
        country_counts = fetch_country_counts(params['start_date'], params['end_date'])
        response_data['country_counts'] = country_counts

    if 'sero_MLST' in params['required_data']:
        sero_MLST_data = process_sero_MLST(params['start_date'], params['end_date'])
        response_data['sero_MLST'] = sero_MLST_data

    if 'country_sero' in params['required_data']:
        country_serodata = country_serotype(params['start_date'], params['end_date'])
        response_data['country_sero'] = country_serodata

    if 'geo_location' in params['required_data']:
        geo_locationdata = geo_dis(params['start_date'], params['end_date'], params['serotype'], params['source'], params['serotype_condition'], params['source_condition'])
        response_data['geo_location'] = geo_locationdata

    if 'process_country_sourcedata' in params['required_data']:
        process_country_sourcedata = process_country_source(params['start_date'], params['end_date'])
        response_data['process_country_sourcedata'] = process_country_sourcedata

    if 'process_mlst_tabledata' in params['required_data']:
        process_mlst_tabledata = process_mlst_table(params['start_date'], params['end_date'])
        response_data['process_mlst_tabledata'] = process_mlst_tabledata

    return JsonResponse(response_data, safe=False, json_dumps_params={'default': str})
# 
    
# -------------------------------------------------FOR ASSAY INFORMATION---------------------------------------------
#     @csrf_exempt
# def update_document(request):
#     es = get_elasticsearch_client()
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             doc_id = data.get('pmcid')

#             # Convert ast to an object if it's a JSON string
#             if 'ast' in data and isinstance(data['ast'], str):
#                 try:
#                     data['ast'] = json.loads(data['ast'])
#                 except json.JSONDecodeError:
#                     return JsonResponse({'status': 'error', 'message': 'Invalid JSON for ast field'}, status=400)
#             # Prepare the script for updating specific fields
#             script = {
#                 "source": "; ".join([f"ctx._source.{key} = params.{key}" for key in data.keys()]),
#                 "lang": "painless",
#                 "params": data
#             }
#             # print(script)
#             # Update the document in Elasticsearch
#             response = es.update(index='sfa', id=doc_id, body={"script": script})
#             # print(response)
#             return JsonResponse({'status': 'success', 'response': response.body}, status=200)
            
#         except Exception as e:
#             logger.error(f"Error updating document: {str(e)}")
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# <--------------------------------------------Individual Process------------------------------------------------------>

#  ------------------------------------------------SEROTYPE-------------------------------------------------------

# def process_serotypes(start_date, end_date):
    es = get_elasticsearch_client()

    # Create the base query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": []
            }
        },
        "aggs": {
            "serotypes": {
                "terms": {
                    "field": "serotype.keyword",  # Ensure this matches the field in your Elasticsearch index
                    "size": 1000  # Increase size to get all serotypes and then filter
                }
            }
        }
    }

    # Add date range filter only if start_date and end_date are provided
    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })

    res = es.search(index="sfa", body=query, size=0)  # Set size to 0 to return only aggregations

    serotype_data = []
    # serotype = [c.strip() for c in serotype.split(',')]
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']  # Initialize serotype within the loop
        
        if serotype != "NA":  # Exclude "NA" serotype
            serotype_count = serotype_bucket['doc_count']
            
            serotype_data.append({
                'name': serotype,
                'value': serotype_count
            })

    # Ensure only unique serotypes are counted correctly
    serotype_data = list({item['name']: item for item in serotype_data}.values())
    
    # Sort serotype data by count in descending order and take the top 10
    serotype_data = sorted(serotype_data, key=lambda x: x['value'], reverse=True)
    
    return serotype_data

#  --------------------------------------------------MLST----------------------------------------------------------

# def process_mlst(start_date, end_date):
    es = get_elasticsearch_client()

    # Create the base query
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match_all": {}}
                ],
                "filter": []
            }
        },
        "aggs": {
            "mlst": {
                "terms": {
                    "field": "mlst.keyword",  # Ensure this matches the field in your Elasticsearch index
                    "size": 1000  # Increase size to get all serotypes and then filter
                }
            }
        }
    }

    # Add date range filter only if start_date and end_date are provided
    if start_date and end_date:
        query["query"]["bool"]["filter"].append({
            "range": {
                "date": {
                    "gte": start_date,
                    "lte": end_date,
                    "format": "yyyy-MM-dd"
                }
            }
        })

    res = es.search(index="sfa", body=query, size=0)  # Set size to 0 to return only aggregations

    mlst_data = []
    for mlst_bucket in res['aggregations']['mlst']['buckets']:
        mlst = mlst_bucket['key'] 
        
        if mlst != "NA": 
            mlst_count = mlst_bucket['doc_count']
            
            mlst_data.append({
                'name': mlst,
                'value': mlst_count
            })

    # Ensure only unique serotypes are counted correctly
    mlst_data = list({item['name']: item for item in mlst_data}.values())
    
    # Sort serotype data by count in descending order and take the top 10
    mlst_data = sorted(mlst_data, key=lambda x: x['value'], reverse=True)
    
    return mlst_data

#  --------------------------------------------------Source----------------------------------------------------------


# def process_source(start_date, end_date):
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }


    query["aggs"] = {
        
    "pmcid": {
        "terms": {"field": "pmcid.keyword", "size": 1000},  
        "aggs": {
                "serotype": {
                    "terms": {"field": "serotype.keyword", "size": 1000},  
                    "aggs": {
                        "source": {
                            "terms": {"field": "source.keyword", "size": 1000},  
                            }
                        }
                    }
                }
             }
    }
    res = es.search(index="sfa", body=query, size=0)

    source_data = []

    for pmc_bucket in res['aggregations']['pmcid']['buckets']:
        for sero_bucket in pmc_bucket['serotype']['buckets']:
            serotype = sero_bucket['key']
            # print("serotype:", serotype)
            if serotype != "NA" and "Salmonella" in serotype:
                        
                for source_bucket in sero_bucket['source']['buckets']:
                    source = source_bucket['key']
                    # print("source", source)
                    if source != "NA": 
                        source_count = source_bucket['doc_count']
                    
                        source_data.append({
                            'name': source,
                            'value': source_count
                        })
    aggregated_data = {}
    for item in source_data:
        name = item['name']
        value = item['value']
        if name in aggregated_data:
            aggregated_data[name]['value'] += value  # Increment the count
        else:
            aggregated_data[name] = item


    source_data = list(aggregated_data.values())

    # source_data = list({item['name']: item for item in source_data}.values())
    # print("source:",source_data)

    source_data = sorted(source_data, key=lambda x: x['value'], reverse=True)

    return source_data



# <--------------------------------------------COUNTRY RELATED------------------------------------------------------>

# def country_serotype(start_date, end_date):
    # es = get_elasticsearch_client()
    
    # # Create the base query
    # query = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {"match_all": {}}
    #             ],
    #             "filter": []
    #         }
    #     },
    #     "aggs": {
    #         "serotypes": {
    #             "terms": {
    #                 "field": "serotype.keyword",
    #                 "size": 1000
    #             },
    #             "aggs": {
    #                 "associated_countries": {
    #                     "terms": {
    #                         "field": "country.keyword",
    #                         "size": 100
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # }

    # if start_date and end_date:
    #     query["query"]["bool"]["filter"].append({
    #         "range": {
    #             "date": {
    #                 "gte": start_date,
    #                 "lte": end_date,
    #                 "format": "yyyy-MM-dd"
    #             }
    #         }
    #     })

    # res = es.search(index="sfa", body=query, size=0)

    # serotype_data = []
    # for serotype_bucket in res['aggregations']['serotypes']['buckets']:
    #     serotype = serotype_bucket['key']
    #     if serotype != "NA":
    #         serotype_count = serotype_bucket['doc_count']
    #         countries = [
    #             {
    #                 'country': country_bucket['key'],
    #             }
    #             for country_bucket in serotype_bucket['associated_countries']['buckets']
    #         ]
    #         serotype_data.append({
    #             'name': serotype,
    #             'value': serotype_count,
    #             'countries': countries
    #         })

    # country_sero = sorted(serotype_data, key=lambda x: x['value'], reverse=True)[:10]
    # return country_sero



# def fetch_country_counts(start_date, end_date):
    # es = get_elasticsearch_client()
    
    # # Create the base query
    # query = {"query": {"match_all": {}}}

    # # Modify the query if start_date and end_date are provided
    # if start_date and end_date:
    #     query = {
    #         "query": {
    #             "range": {
    #                 "date": {
    #                     "gte": start_date,
    #                     "lte": end_date,
    #                     "format": "yyyy-MM-dd"
    #                 }
    #             }
    #         }
    #     }

    # res = es.search(index="sfa", body=query, size=10000)
    # country_counts = {}
    
    # delimiter_pattern = re.compile(r'(?<=\s)(?:and|,|;)(?=\s)|^and\s|,|;$')

    # for hit in res['hits']['hits']:

    #     country = hit['_source'].get('country')
    #     if country:
    #         countries = delimiter_pattern.split(country)
    #         for c in countries:
    #             c = c.strip()
    #             if c in country_counts:
    #                 country_counts[c] += 1
    #             else:
    #                 country_counts[c] = 1


    # top_countries = dict(Counter(country_counts).most_common(10))

    # return top_countries

# def process_sero_MLST(start_date, end_date):
    es = get_elasticsearch_client()

    query = {"query": {"match_all": {}}}

    if start_date and end_date:
        query = {
            "query": {
                "range": {
                    "date": {
                        "gte": start_date,
                        "lte": end_date,
                        "format": "yyyy-MM-dd"
                    }
                }
            }
        }

    # Add aggregation for serotypes and MLST
    query["aggs"] = {
        "serotypes": {
            "terms": {"field": "serotype.keyword", "size": 1000},  # Top 10 Serotypes
            "aggs": {
                "top_mlst": {
                    "terms": {"field": "mlst.keyword", "size": 3000}  # Top 3 MLST per serotype
                }    
            }
        }
    }

    res = es.search(index="sfa", body=query, size=0)
    # serotype = [c.strip() for c in serotype.split(',')]
    serotype_MLST_data = []
    for serotype_bucket in res['aggregations']['serotypes']['buckets']:
        serotype = serotype_bucket['key']

        if serotype != "NA":
            serotype_count = serotype_bucket['doc_count']  # Count of documents for this serotype
            mlst_buckets = serotype_bucket['top_mlst']['buckets']
            mlst_data = [{'mlst': mlst['key'], 'count': mlst['doc_count']} for mlst in mlst_buckets]
            
            serotype_MLST_data.append({
                'serotype': serotype,
                'count': serotype_count,  # Include the count in the result
                'mlst': mlst_data
            })

    return serotype_MLST_data