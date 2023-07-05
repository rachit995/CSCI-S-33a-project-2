from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path(
        "toggle_watchlist/<int:listing_id>",
        views.toggle_watchlist,
        name="toggle_watchlist",
    ),
    path("add_bid/<int:listing_id>", views.add_bid, name="add_bid"),
    path(
        "add_comment/<int:listing_id>", views.add_comment, name="add_comment"
    ),
    path(
        "close_listing/<int:listing_id>",
        views.close_listing,
        name="close_listing",
    ),
    path("categories/<str:category>", views.category, name="category"),
    path("user/<str:username>", views.user, name="user"),
]
