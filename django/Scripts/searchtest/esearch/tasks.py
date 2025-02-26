from celery import shared_task
from django.core.cache import cache
from .views import (
    process_serotypes,
    process_mlst,
    process_source,
    country_serotype,
    fetch_country_counts,
    process_sero_MLST,
    geo_dis,
    process_country_source,
    process_mlst_table,
    process_ID_sero,
    process_ID_MLST,
    geo_dis_assay
)

@shared_task
def pre_process_data(): 
    default_start_date = '1900-01-01'
    default_end_date = '2024-01-01'
    default_serotype = None  
    default_source = None  

    serotype_data =process_serotypes(default_start_date, default_end_date)
    cache.set(f'serotype_data_{default_start_date}_{default_end_date}', serotype_data, timeout=60*60)

    mlst_data = process_mlst(default_start_date, default_end_date)
    cache.set(f'mlst_data_{default_start_date}_{default_end_date}', mlst_data, timeout=60*60)

    source_data = process_source(default_start_date, default_end_date)
    cache.set(f'source_data_{default_start_date}_{default_end_date}', source_data, timeout=60*60)

    country_sero_data = country_serotype(default_start_date, default_end_date)
    cache.set(f'country_sero_data_{default_start_date}_{default_end_date}', country_sero_data, timeout=60*60)

    country_counts = fetch_country_counts(default_start_date, default_end_date)
    cache.set(f'country_counts_{default_start_date}_{default_end_date}', country_counts, timeout=60*60)

    sero_MLST_data = process_sero_MLST(default_start_date, default_end_date)
    cache.set(f'sero_MLST_data_{default_start_date}_{default_end_date}', sero_MLST_data, timeout=60*60)

    geo_location_data = geo_dis(default_start_date, default_end_date, default_serotype, default_source, None, None)
    cache_key_suffix = f"{default_start_date}_{default_end_date}_{default_serotype}_{default_source}"
    cache.set(f'geo_location_data_{cache_key_suffix}', geo_location_data, timeout=60*60)

    geo_location_data2 = geo_dis_assay(default_start_date, default_end_date, default_serotype, default_source, None, None)
    cache_key_suffix = f"{default_start_date}_{default_end_date}_{default_serotype}_{default_source}"
    cache.set(f'geo_location_data2_{cache_key_suffix}', geo_location_data2, timeout=60*60)

    country_source_data = process_country_source(default_start_date, default_end_date)
    cache.set(f'country_source_data_{default_start_date}_{default_end_date}', country_source_data, timeout=60*60)

    mlst_table_data = process_mlst_table(default_start_date, default_end_date)
    cache.set(f'mlst_table_data_{default_start_date}_{default_end_date}', mlst_table_data, timeout=60*60)

    ID_sero_data = process_ID_sero(default_start_date, default_end_date)
    cache.set(f'ID_sero_data_{default_start_date}_{default_end_date}', ID_sero_data, timeout=60*60)

    ID_MLST_data = process_ID_MLST(default_start_date, default_end_date)
    cache.set(f'ID_MLST_data_{default_start_date}_{default_end_date}', ID_MLST_data, timeout=60*60)





