from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_hours_URL, name="get_hours_URL"),
    path("get_hours_URL/", views.get_hours_URL, name="get_hours_URL"),
    path(
        "display_hours/<int:location_id>/<str:orientation>",
        views.display_hours,
        name="display_hours",
    ),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
]
