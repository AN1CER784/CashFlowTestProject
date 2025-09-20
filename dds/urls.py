from django.urls import path
from . import views
app_name = 'dds'

urlpatterns = [
    path('', views.records_app, name='record-list'),
    path('dictionaries/', views.dictionaries_app, name='dictionaries'),
]
