from django.urls import path
from . import views


urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login_view, name = "login"),
    path("", views.index, name = "index"),
    path("createlisting", views.create_listing, name = "createlisting" ),
    path("details/<str:id>", views.title, name = "title"),
    path("closedlisting", views.closed_listing, name = "closedlisting"),
    path("<str:id>/remove", views.remove, name = "remove"),
    path("logout", views.logout_view, name="logout")

]