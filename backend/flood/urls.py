from django.urls import path
from . import views

urlpatterns = [
    path("predict/", views.predict, name="predict"),
    path("roads/", views.roads, name="roads"),
    path("retrain/", views.retrain, name="retrain"),
]
