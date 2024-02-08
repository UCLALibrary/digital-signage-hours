from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_hours_url, name="get_hours_url"),
    path("get_hours_url/", views.get_hours_url, name="get_hours_url"),
    path(
        "display_hours/<int:location_id>/<str:orientation>",
        views.display_hours,
        name="display_hours",
    ),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
]
