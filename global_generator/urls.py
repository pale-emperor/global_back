from django.urls import path
from . import views

urlpatterns = [
    path('generate', views.generate_global),
    path('json', views.outjson),
    path('', views.index),
    path('index', views.index)
]
