from django.urls import path
from . import views

urlpatterns = [
    path('predictions/', views.predictions, name='predictions'),
    path('roads/', views.roads, name='roads'),  # <-- new debug endpoint
]
