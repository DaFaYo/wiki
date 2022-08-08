from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry_name"),
    path("search_results", views.search_entry, name="search"),
    path("create_page", views.add_new_entry, name="create_new_page"),
    path("edit_page/<str:title>", views.edit_entry, name="edit_page"),
    path("random_page", views.get_random_page, name="get_random_page")
]
