from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet

router = DefaultRouter()
router.register(r'', CompanyViewSet)

urlpatterns = router.urls + [
    path('signup/', CompanyViewSet.as_view({'post': 'signup'}), name='company-signup'),
    path('login/', CompanyViewSet.as_view({'post': 'login'}), name='company-login'),
    path('get_api/', CompanyViewSet.as_view({'post': 'get_api'}), name='get-api'),
    path('refreshdashboard/', CompanyViewSet.as_view({'post': 'refresh_dashboard'}), name='refresh-dashboard'),
    path('kyc-user/', CompanyViewSet.as_view({'post': 'check_user'}), name='check-user'),
    path('add-user/', CompanyViewSet.as_view({'post': 'add_user'}), name='add-user'),
]
