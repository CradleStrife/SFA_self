from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import json, re
from django.conf import settings
from elasticsearch_dsl.utils import AttrList

# --------------------------------------FOR LOCAL DATA -------------------------------------------------------------------

def esearch_local(**kwargs):
    print("esearch_local")
    client = Elasticsearch(settings.ELASTICSEARCH_URL)
    index_name = 'local'
    must_queries = []

    for field, value in kwargs.items():
        if value:  # Only add non-empty values
            must_queries.append(Q("match", **{field: value}))

    if must_queries:
        q = Q("bool", must=must_queries)
    else:
        q = Q("match_all")  # Return all documents if no parameters are provided

    s = Search(using=client, index=index_name).query(q)[0:500]
    response = s.execute()
        
    return get_results(response)


def esearch_local_clustering(**kwargs):
    from elasticsearch import Elasticsearch
    from django.conf import settings
    from elasticsearch_dsl import Search, Q

    import logging
    logger = logging.getLogger(__name__)

    # 在查询之前
    logger.debug(f"Search parameters: {kwargs}")

    client = Elasticsearch(settings.ELASTICSEARCH_URL)
    index_name = 'local'
    must_queries = []

    for field, value in kwargs.items():
        if value:  # Only add non-empty values
            must_queries.append(Q("match", **{field: value}))

    if must_queries:
        q = Q("bool", must=must_queries)
    else:
        q = Q("match_all")  # Return all documents if no parameters are provided

    s = Search(using=client, index=index_name).query(q)[0:7000]
    response = s.execute()

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
        }
        results.append(result)
    # 在返回结果之前
    logger.debug(f"Number of hits: {len(results)}")

    return results

# def esearch_local(**kwargs):
#     from elasticsearch import Elasticsearch
#     from django.conf import settings
#     from elasticsearch_dsl import Search, Q

#     import logging
#     logger = logging.getLogger(__name__)

#     # 在查询之前
#     logger.debug(f"Search parameters: {kwargs}")

#     client = Elasticsearch(settings.ELASTICSEARCH_URL)
#     index_name = 'local'
#     must_queries = []

#     for field, value in kwargs.items():
#         if value:  # Only add non-empty values
#             must_queries.append(Q("match", **{field: value}))

#     if must_queries:
#         q = Q("bool", must=must_queries)
#     else:
#         q = Q("match_all")  # Return all documents if no parameters are provided

#     s = Search(using=client, index=index_name).query(q)[0:7000]
#     response = s.execute()

#     # 提取结果
#     results = []
#     for hit in response:
#         hit_dict = hit.to_dict()
#         result = {
#             'ID': hit_dict.get('ID', []),
#             'Source': hit_dict.get('Source', []),
#             'Date': hit_dict.get('Date', []),
#             'Country': hit_dict.get('Country', []),
#             'Brand': hit_dict.get('Brand', []),
#             'Serotype': hit_dict.get('Serotype', []),
#             'MLST': hit_dict.get('MLST', []),
#             'AST': hit_dict.get('AST', []),
#             'SPI': hit_dict.get('SPI', []),
#             'AMR': hit_dict.get('AMR', []),
#             'plasmid': hit_dict.get('plasmid', []),
#             # 包含其他需要的属性
#         }
#         results.append(result)
#     # 在返回结果之前
#     logger.debug(f"Number of hits: {len(results)}")

#     return results


def get_results(response):
    results = []
    for hit in response:
        # Check if hit.AST is "NA" and set it to {"NA": "NA"} if true
        print(hit.AST)
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
def esearch_assay_old(**kwargs):
    client = Elasticsearch(settings.ELASTICSEARCH_URL)
    index_name = 'assay_data'  # Change this to your actual assay index name
    must_queries = []
    print(kwargs.items())

    for field, value in kwargs.items():
        if value:  # Only add non-empty values
            must_queries.append(Q("match", **{field: value}))

    print(must_queries)
    if must_queries:
        q = Q("bool", must=must_queries)
    else:
        q = Q("match_all")  # Return all documents if no parameters are provided

    s = Search(using=client, index=index_name).query(q)[0:50]
    response = s.execute()
    print('response: ', response)
    return get_results_assay(response)  # Use a separate get_results for assay if structure is different

def esearch_assay(**kwargs):
    client = Elasticsearch(settings.ELASTICSEARCH_URL)
    index_name = 'salmonella-assay-index-v4'  # Change this to your actual assay index name
    print("kwargs: ",kwargs.items())

    must_queries = []
    must_queries_no_isolates = []
    must_queries_isolates = []

    must_args_big=['pmcid']
    must_args_small=['isolate_id','isolate_source','isolate_country','serotype']

    for arg in must_args_big:
        if arg in kwargs:
            must_queries.append(Q("match", **{arg: kwargs.get(arg)}))
    for arg in must_args_small:
        if arg in kwargs:
            must_queries_no_isolates.append(Q('nested',path='no_isolates_only_assayinformation',query=Q('match',**{f'no_isolates_only_assayinformation.{arg}':kwargs.get(arg)})))
            must_queries_isolates.append(Q('nested',path='isolates_with_linking',query=Q('match',**{f'isolates_with_linking.{arg}':kwargs.get(arg)})))

  
    print('must_queries: ', must_queries)
    print('must_queries_no_isolates: ', must_queries_no_isolates)
    print('must_queries_isolates: ', must_queries_isolates)
    
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
    s = Search(using=client, index=index_name).query(q)[0:50]
    print(s.to_dict())
    response = s.execute()
    print('response count: ', len(response))
    return get_results_assay(response)  # Use a separate get_results for assay if structure is different  

def get_results_assay(response):
    results=[]
    for hit in response:
        hit_dict=hit.to_dict()
        if 'no_isolates_only_assayinformation' in hit_dict and 'isolate_country' in hit_dict['no_isolates_only_assayinformation']:
            # print(hit_dict['no_isolates_only_assayinformation']['isolate_country'])
            if hit_dict['no_isolates_only_assayinformation']['isolate_country']=='Viet Nam':
                hit_dict['no_isolates_only_assayinformation']['isolate_country']='Vietnam'
        if 'isolates_with_linking' in hit_dict:
            for isolate in hit_dict['isolates_with_linking']:
                if 'isolate_country' in isolate:
                    # print(isolate['isolate_country'])
                    if isolate['isolate_country']=='Viet Nam':
                        isolate['isolate_country']='Vietnam'
        results.append(hit_dict)
    return results





def get_results_assay_old(response):
    results = []
    for hit in response:
        print(hit)
        countryname = getattr(hit, 'countryname', None)
        print(countryname)
        # Skip if countryname is None, empty, or 'na'
        if not countryname or countryname.lower() == 'na':
            continue
        if countryname == "Viet Nam":
               countryname = "Vietnam"
        countryname = re.sub(r"\s*\(.*?\)\s*", "", countryname).strip()
        if "and" in countryname:
            countryname = countryname.split(" and ")
            for countryname in countryname:
                countryname = countryname.strip()
        result_tuple = (         
            hit.pmid,  # PubMed ID
            hit.pmcid,  # PubMed Central ID
            hit.title,  # Title of the paper
            hit.abstract,  # Abstract of the paper
            hit.authors,  # Authors of the paper
            hit.journal,  # Journal name
            hit.year,  # Year of publication
            hit.url,  # URL link to the paper
            hit.doi,  # DOI of the paper
            hit.key_words,  # Keywords related to the paper
            hit.filename,  # Filename for the document
            hit.isolate_id,  # ID of the isolate
            hit.isolate_source,  # Source of the isolate
            hit.isolate_date,  # Date of the isolate
            hit.isolate_country,  # Country of the isolate
            hit.serotype,  # Serotype information
            hit.mlst,  # Multilocus sequence typing (MLST)
            hit.ast_data,  # AST data, as nested serotype and antibiotics
            hit.spi,  # SPI (Salmonella Pathogenicity Islands)
            hit.amr,  # Antimicrobial resistance
            hit.plasmid,  # Plasmid information
            hit.snp,  # Single Nucleotide Polymorphisms
            hit["virulence genes"],  # Virulence genes information
            hit["accession numbers"],  # Accession numbers
            hit.final_cleaned_text,  # Cleaned final text of the document
            hit["accession numbers_merge"],  # Merged accession numbers
            countryname
        )
        results.append(result_tuple)
        print("processed one hit")
    print('processed results count: ',len(results))
    return results

# def esearch_assay(**kwargs):
#     from elasticsearch import Elasticsearch
#     from django.conf import settings
#     from elasticsearch_dsl import Search, Q
#     import logging
#     logger = logging.getLogger(__name__)

#     # 在查询之前
#     logger.debug(f"Search parameters: {kwargs}")

#     client = Elasticsearch(settings.ELASTICSEARCH_URL)
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




