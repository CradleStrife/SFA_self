from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError

def health(request):
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        return JsonResponse({'status': 'DOWN'})
    return JsonResponse({'status': 'UP'})
