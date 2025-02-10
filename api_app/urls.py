from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get-file-names", views.get_file_names, name="fileBrowser"),
    path("<str:file_id>", views.file_browser, name="fileBrowser"),
]