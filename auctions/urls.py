from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),  # Index page
    path("login", views.login_view, name="login"),  # Login page
    path("logout", views.logout_view, name="logout"),  # Logout page
    path("register", views.register, name="register"),  # Register page
    path("create", views.create_listing, name="create"),  # Create listing page
    path(
        "listing/<int:listing_id>", views.listing_item_view, name="listing"
    ),  # Listing page
    path(
        "watchlist", views.watchlist_view, name="watchlist"
    ),  # Watchlist page
    path("categories", views.categories_list_view, name="categories"),
    path(
        "toggle_watchlist/<int:listing_id>",
        views.toggle_watchlist,
        name="toggle_watchlist",
    ),  # API endpoint to toggle watchlist
    path(
        "add_bid/<int:listing_id>", views.add_bid, name="add_bid"
    ),  # API endpoint to add bid
    path(
        "add_comment/<int:listing_id>", views.add_comment, name="add_comment"
    ),  # API endpoint to add comment
    path(
        "close_listing/<int:listing_id>",
        views.close_listing,
        name="close_listing",
    ),  # API endpoint to close listing
    path(
        "categories/<str:category>", views.category_item_view, name="category"
    ),  # Category page
    path(
        "user/<str:username>", views.user_listings_view, name="user"
    ),  # User page
]
