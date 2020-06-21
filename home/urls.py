from django.urls import path
from . import views # need to import views from the current directory

urlpatterns = [
    path('', views.index, name='home')
]
