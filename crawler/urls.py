from django.urls import path
from . import views

urlpatterns = [
	path('', views.index),
	path('api/crawler', views.crawler, name="crawling"),
]