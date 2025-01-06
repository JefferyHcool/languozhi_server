from django.urls import path
from .views import get_public_key

urlpatterns = [
    path('get-public-key/', get_public_key, name='get_public_key'),
]
