from rest_framework.routers import DefaultRouter

from api.products.views import ProductsViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductsViewSet, basename="api-products")
router.register(r'categories', CategoryViewSet, basename="api-categories")
urlpatterns = router.urls
