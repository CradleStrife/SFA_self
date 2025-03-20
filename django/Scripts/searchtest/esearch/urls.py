from django.urls import path 
from . import views 
app_name = 'esearch' 
# urlpatterns = [ path('', views.search_index, name='search_view'),
#                path('get-country-data/', views.country_data, name='get-country-data'),
#                path('enquiry/', views.enquiry, name='enquiry'),
#                path('result/', views.result, name='result'),]
urlpatterns = [
    path('api/search/', views.search_index, name='search_index'),
    path('api/update_document/',views.update_document,name='update_document'),
    path('api/upload/', views.upload_files, name='upload_files'),
    path('api/list/', views.list_files, name='list_files'),
    path('api/search_clustering/', views.search_index_clustering, name='search_index_clustering'),

    ###########################
    #Frank!!!
    path('api/upload2temp/',views.upload2temp,name='upload2temp'),
    path('api/getTempData/',views.getTempData,name='getTempData'),
    path('api/confirmTemp2es/',views.confirmTemp2es,name='confirmTemp2es'),
    path('api/deleteTempData/',views.deleteTempData,name='deleteTempData'),

    path('api/simple_search/',views.simple_search,name='simple_search'),
    path('api/clear_cache/',views.clear_cache,name='clear_cache')
    ###########################

]