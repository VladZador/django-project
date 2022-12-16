from django.urls import path

from api.products.views import ProductsListView, ProductRetrieveView

urlpatterns = [
    path('products/', ProductsListView.as_view()),
    path('products/<uuid:pk>/', ProductRetrieveView.as_view()),
]
