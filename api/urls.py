from django.urls import path, include
from api.products.urls import urlpatterns as products_urlpatterns


urlpatterns = [
    path('', include(products_urlpatterns)),
    path('api-auth/', include('rest_framework.urls')),
]
