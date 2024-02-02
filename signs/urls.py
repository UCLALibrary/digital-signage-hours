from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_URL, name="get_URL"),
    path("get_URL/", views.get_URL, name="get_URL"),
    path("display/<int:location_id>/<str:orientation>", views.display, name="display"),
]
