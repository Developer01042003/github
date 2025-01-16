from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = router.urls + [
    path('signup/', UserViewSet.as_view({'post': 'signup'}), name='signup'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('kyckey/', UserViewSet.as_view({'post': 'kycShareKey'}), name='getkyckey'),
    path('uniquekey/', UserViewSet.as_view({'post': 'getUniqueKey'}), name='getuniquekey'),
    path(
        'mintnft/',
        UserViewSet.as_view({'post': 'nft_create'}),
        name='nftuniquekey'
    ),
    path('dashboard/', UserViewSet.as_view({'post': 'dashboard'}), name='dashboard'),
]