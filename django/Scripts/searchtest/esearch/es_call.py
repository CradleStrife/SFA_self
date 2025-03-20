from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import json, re
from django.conf import settings
from elasticsearch_dsl.utils import AttrList
from .utili import get_elasticsearch_client
# --------------------------------------FOR LOCAL DATA -------------------------------------------------------------------

def esearch_simple(index_name, field_name, value):
    client = get_elasticsearch_client()
    s = Search(using=client, index=index_name).query("match", **{field_name: value})[0]
    response = s.execute()
    return get_results_simple(response)

def esearch_local(**kwargs):
    # print("esearch_local")
    client = get_elasticsearch_client()
    index_name = 'local'
    must_queries = []

    print("kwargs: ",kwargs.items())

    for field, value in kwargs.items():
        if value:  # Only add non-empty values
            must_queries.append(Q("match", **{field: value}))

    if len(must_queries)>0:
        q = Q("bool", must=must_queries)
    else:
        q = Q("match_all")  # Return all documents if no parameters are provided

    s = Search(using=client, index=index_name).query(q)[0:7000]
    response = s.execute()
        
    return get_results(response)


def esearch_local_clustering(**kwargs):
    client = get_elasticsearch_client()
    index_name = 'local'
    must_queries = []
    for field, value in kwargs.items():
        if value:  # Only add non-empty values
            must_queries.append(Q("match", **{field: value}))

    if must_queries:
        q = Q("bool", must=must_queries)
        print("must queries:",must_queries)
    else:
        q = Q("match_all")  # Return all documents if no parameters are provided
        print("match all")

    s = Search(using=client, index=index_name).query(q)
    response = s.execute()
    print("response length",len(response))
    # 提取结果
    results = []
    for hit in response:
        hit_dict = hit.to_dict()
        result = {
            'ID': hit_dict.get('ID', []),
            'Source': hit_dict.get('Source', []),
            'Date': hit_dict.get('Date', []),
            'Country': hit_dict.get('Country', []),
            'Brand': hit_dict.get('Brand', []),
            'Serotype': hit_dict.get('Serotype', []),
            'MLST': hit_dict.get('MLST', []),
            'AST': hit_dict.get('AST', []),
            'SPI': hit_dict.get('SPI', []),
            'AMR': hit_dict.get('AMR', []),
            'plasmid': hit_dict.get('plasmid', []),
            # 包含其他需要的属性
            'index_name':"local"
        }
        results.append(result)
    return results


def esearch_assay_clustering(**kwargs):
    assay_index_name=kwargs["assay_index_name"]
    results=esearch_assay(**kwargs)
    isolates=[]
    processed_results=[]
    for result in results:
        isolates=get_isolates_from_assay(result)
        for isolate in isolates:
            processed_result=get_processed_result_from_isolate(result["pmcid"],isolate)
            processed_result["index_name"]=assay_index_name
            processed_results.append(processed_result)
    return processed_results

def get_processed_result_from_isolate(pmcid,isolate):
    return {
        'ID': [pmcid],
        'Source': [isolate.get("isolate_source","")],
        'Date': [isolate.get("isolate_date","1000")],
        'Country': [isolate.get("isolate_country","")],
        'Brand': [""],
        'Serotype': [isolate.get("serotype","")],
        'MLST': [isolate.get("mlst","")],
        'AST': [isolate.get('ast_data',"")],
        'SPI': [isolate.get('spi',"")],
        'AMR': [isolate.get("amr","")],
        'plasmid': [isolate.get("plasmid","")]
    }

def get_isolates_from_assay(assay):
    isolates=[]
    if "isolates_with_linking" in assay and assay["isolates_with_linking"]:
        isolates+=assay["isolates_with_linking"]
    if "no_isolates_only_assayinformation" in assay and assay["no_isolates_only_assayinformation"]:
        isolates.append(assay["no_isolates_only_assayinformation"])
    return isolates

def get_results(response):
    results = []
    for hit in response:
        # Check if hit.AST is "NA" and set it to {"NA": "NA"} if true
        # print(hit.AST)
        if hit.AST == "NA":
            formatted_ast = {"NA": "NA"}
        else:
            # Convert AST to dictionary if it's a list
            ast = hit.AST
            if isinstance(ast, AttrList):
                ast = list(ast)
            if isinstance(ast, list):
                formatted_ast = {}
                for item in ast:
                    if hasattr(item, 'to_dict'):
                        item = item.to_dict()
                    if isinstance(item, dict):
                        for key, value in item.items():
                            formatted_ast[key] = value
            else:
                # Handle the case where ast is not a list
                formatted_ast = ast
        Date = hit.Date[0]
        Country = hit.Country[0]
        AST_a = formatted_ast
        
        result_tuple = (hit.ID, hit.Source, Date, Country, hit.Brand, hit.Serotype, hit.MLST, AST_a, hit.SPI, hit.AMR, hit.plasmid)
        results.append(result_tuple)
    return results



#  --------------------------------for ASSAY INFORMATION -----------------------------------------------------------------

def esearch_assay(**kwargs):
    client = get_elasticsearch_client()
    index_name = kwargs.get('assay_index_name','salmonella-assay-index-v4')   # default 'salmonella-assay-index-v4'  
    del kwargs['assay_index_name']
    # print("kwargs: ",kwargs.items())

    must_queries = []
    must_queries_no_isolates = []
    must_queries_isolates = []

    must_args_big=['pmcid']
    must_args_small=['isolate_id','isolate_source','isolate_country','serotype','mlst']

    for arg in must_args_big:
        if arg in kwargs:
            must_queries.append(Q("match", **{arg: kwargs.get(arg)}))
    for arg in must_args_small:
        if arg in kwargs:
            # must_queries_no_isolates.append(Q('nested',path='no_isolates_only_assayinformation',query=Q('match',**{f'no_isolates_only_assayinformation.{arg}':kwargs.get(arg)})))
            # must_queries_isolates.append(Q('nested',path='isolates_with_linking',query=Q('match',**{f'isolates_with_linking.{arg}':kwargs.get(arg)})))
            must_queries_no_isolates.append(Q('match',**{f'no_isolates_only_assayinformation.{arg}':kwargs.get(arg)}))
            must_queries_isolates.append(Q('match',**{f'isolates_with_linking.{arg}':kwargs.get(arg)}))


  
    # print('must_queries: ', must_queries)
    # print('must_queries_no_isolates: ', must_queries_no_isolates)
    # print('must_queries_isolates: ', must_queries_isolates)
    
    should_queries = Q("bool", should=[
        Q("bool",must=must_queries_no_isolates), 
        Q("bool",must=must_queries_isolates)
    ])
    
    must_q=Q("bool",must=must_queries)
    should_q=Q("bool",should=should_queries)
    combined_q=[]
    if must_q:
        combined_q.append(must_q)
    if should_q:
        combined_q.append(should_q)
    q = Q("bool", must=combined_q)
    s = Search(using=client, index=index_name).query(q)[0:10000]
    # # print(s.to_dict())
    response = s.execute()
    # print('response count: ', len(response))
    return get_results_assay(response)  # Use a separate get_results for assay if structure is different  


def get_results_simple(response):
    results=[]
    for hit in response:
        hit_dict=hit.to_dict()
        results.append(hit_dict)
    return results
def get_results_assay(response):
    results=[]
    for hit in response:
        hit_dict=hit.to_dict()
        if 'no_isolates_only_assayinformation' in hit_dict and 'isolate_country' in hit_dict['no_isolates_only_assayinformation']:
            # # print(hit_dict['no_isolates_only_assayinformation']['isolate_country'])
            if hit_dict['no_isolates_only_assayinformation']['isolate_country']=='Viet Nam':
                hit_dict['no_isolates_only_assayinformation']['isolate_country']='Vietnam'
        if 'isolates_with_linking' in hit_dict:
            for isolate in hit_dict['isolates_with_linking']:
                if 'isolate_country' in isolate:
                    # # print(isolate['isolate_country'])
                    if isolate['isolate_country']=='Viet Nam':
                        isolate['isolate_country']='Vietnam'
        results.append(hit_dict)
    return results




# def esearch_assay(**kwargs):
#     from elasticsearch import Elasticsearch
#     from django.conf import settings
#     from elasticsearch_dsl import Search, Q
#     import logging
#     logger = logging.getLogger(__name__)

#     # 在查询之前
#     logger.debug(f"Search parameters: {kwargs}")

#     client = get_elasticsearch_client()
#     index_name = 'assay_data'  # 全局数据存储的索引名称
#     must_queries = []

#     for field, value in kwargs.items():
#         if value:  # 仅添加非空值
#             must_queries.append(Q("match", **{field: value}))

#     if must_queries:
#         q = Q("bool", must=must_queries)
#     else:
#         q = Q("match_all")  # 如果未提供任何参数，则返回所有文档

#     s = Search(using=client, index=index_name).query(q)[0:7000]
#     response = s.execute()

#     # 提取结果
#     results = []
#     for hit in response:
#         hit_dict = hit.to_dict()
#         result = {
#             'ID': hit_dict.get('isolate_id', []),
#             'Source': hit_dict.get('isolate_source', []),
#             'Date': hit_dict.get('isolate_date', []),
#             'Country': hit_dict.get('isolate_country', []),
#             'Brand': hit_dict.get('brand', []),
#             'Serotype': hit_dict.get('serotype', []),
#             'MLST': hit_dict.get('mlst', []),
#             'AST': hit_dict.get('ast_data', []),
#             'SPI': hit_dict.get('spi', []),
#             'AMR': hit_dict.get('amr', []),
#             'plasmid': hit_dict.get('plasmid', []),
#             # 包含其他需要的属性
#         }
#         results.append(result)

#     # 在返回结果之前
#     logger.debug(f"Number of hits: {len(results)}")

#     return results




