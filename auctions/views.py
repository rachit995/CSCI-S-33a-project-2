from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .utils import filter_objects

from .models import User, Category, Listing, Bid, Comment, Watchlist

login_url = "login"


def index(request):
    """
    Returns the index page with all active listings and the filter and search

    :param request: HTTP request
    :return: index page with all active listings
    """
    listings = Listing.objects.all()
    listing_filter = request.GET.get("filter", "active")
    query = request.GET.get("q", "")
    listings = filter_objects(request, listings, listing_filter, query)
    return render(
        request,
        "auctions/index.html",
        {"listings": listings, "filter": listing_filter, "query": query},
    )


def login_view(request):
    """
    Logs in the user if the username and password are correct.

    :param request: HTTP request
    :return: index page if login successful, login page if login unsuccessful

    Not using Django forms because this was already implemented in the
    distribution code.
    """
    # If user is already logged in, redirect to redirect url or index page
    next_page = request.GET["next"] if "next" in request.GET else None
    if request.user.is_authenticated:
        if next_page:
            return HttpResponseRedirect(next_page)
        else:
            return HttpResponseRedirect(reverse("index"))
    else:
        if request.method == "POST":
            # Attempt to sign user in
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                if next_page:
                    return HttpResponseRedirect(next_page)
                else:
                    return HttpResponseRedirect(reverse("index"))
            else:
                return render(
                    request,
                    "auctions/login.html",
                    {"message": "Invalid username and/or password."},
                )
        else:
            return render(request, "auctions/login.html")


def logout_view(request):
    """
    Logs out the user.

    :param request: HTTP request
    :return: index page
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Registers a new user.

    :param request: HTTP request
    :return: index page if registration successful, registration page if
    registration unsuccessful

    Not using Django forms because this was already implemented in the
    distribution code.
    """
    # If user is already logged in, redirect to index page
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure username and email are not empty
        if not username:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username cannot be empty."},
            )

        if not email:
            return render(
                request,
                "auctions/register.html",
                {"message": "Email cannot be empty."},
            )

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not password:
            return render(
                request,
                "auctions/register.html",
                {"message": "Password cannot be empty."},
            )
        if not confirmation:
            return render(
                request,
                "auctions/register.html",
                {"message": "Confirmation cannot be empty."},
            )

        if password != confirmation:
            return render(
                request,
                "auctions/register.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url=login_url)
def create_listing(request):
    """
    Creates a new listing.

    :param request: HTTP request
    :return: index page if creation successful, create listing page if creation
    unsuccessful
    """

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        category = Category.objects.get(category=request.POST["category"])
        # Ensure title, description, starting_bid and category are not empty
        if not title:
            messages.error(
                request,
                "Title cannot be empty.",
            )
        if not description:
            messages.error(
                request,
                "Description cannot be empty.",
            )
        if not starting_bid:
            messages.error(
                request,
                "Starting bid cannot be empty.",
            )
        if not category:
            messages.error(
                request,
                "Category cannot be empty.",
            )
        if title and description and starting_bid and category:
            try:
                listing = Listing(
                    title=title,
                    description=description,
                    image_url=image_url,
                    starting_bid=starting_bid,
                    category=category,
                    user=request.user,
                )
                listing.save()
            except IntegrityError:
                messages.error(
                    request,
                    "Listing already exists.",
                )
                return render(request, "auctions/create_listing.html")
            return HttpResponseRedirect(reverse("index"))
    return render(
        request,
        "auctions/create_listing.html",
        {"categories": Category.objects.all()},
    )


def listing_item_view(request, listing_id):
    """
    Returns the listing page.

    :param request: HTTP request
    :param listing_id: listing id
    :return: listing page
    """

    listing = Listing.objects.get(pk=listing_id)
    return render(
        request,
        "auctions/listing_item.html",
        {
            "listing": listing,
            "bids": listing.bids.all(),
            "comments": listing.get_comments(),
        },
    )


@login_required(login_url=login_url)
def watchlist_view(request):
    """
    Returns the watchlist page.

    :param request: HTTP request
    :return: watchlist page
    """

    listings = Listing.objects.filter(watchlists__user=request.user)
    listing_filter = request.GET.get("filter", "active")
    query = request.GET.get("q", "")
    listings = filter_objects(request, listings, listing_filter, query)
    return render(
        request,
        "auctions/watchlist.html",
        {
            "listings": listings,
            "filter": listing_filter,
            "query": query,
        },
    )


def categories_list_view(request):
    """
    Returns the categories page.

    :param request: HTTP request
    :return: categories page
    """

    categories = Category.objects.all()
    return render(
        request, "auctions/categories.html", {"categories": categories}
    )


def category_item_view(request, category):
    """
    Returns the category page.

    :param request: HTTP request
    :param category: category name
    :return: category page
    """
    category = Category.objects.get(category=category)
    listings = Listing.objects.filter(category=category)
    listing_filter = request.GET.get("filter", "active")
    query = request.GET.get("q", "")
    listings = filter_objects(request, listings, listing_filter, query)
    return render(
        request,
        "auctions/category.html",
        {
            "category": category,
            "listings": listings,
            "query": query,
            "filter": listing_filter,
        },
    )


@login_required(login_url=login_url)
def toggle_watchlist(request, listing_id):
    """
    Toggles the watchlist.

    :param request: HTTP request
    :param listing_id: listing id
    :return: listing page
    """

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        if request.user == listing.user:
            messages.error(
                request,
                "You cannot add your own listing to your watchlist.",
            )
            return HttpResponseRedirect(
                reverse(
                    "listing",
                    args=(listing_id,),
                )
            )
        if Watchlist.objects.filter(
            listing=listing, user=request.user
        ).exists():
            Watchlist.objects.filter(
                listing=listing, user=request.user
            ).delete()
            messages.info(
                request,
                "Listing removed from watchlist.",
            )
        else:
            watchlist = Watchlist(listing=listing, user=request.user)
            watchlist.save()
            messages.info(
                request,
                "Listing added to watchlist.",
            )
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url=login_url)
def add_bid(request, listing_id):
    """
    Adds a bid to the listing.

    :param request: HTTP request
    :param listing_id: listing id
    :return: listing page
    """

    listing = Listing.objects.get(pk=listing_id)
    bid = int(request.POST["bid"])
    if bid < listing.starting_bid:
        messages.error(
            request,
            "Bid must be greater than starting bid.",
        )
        return HttpResponseRedirect(
            reverse(
                "listing",
                args=(listing_id,),
            )
        )
    if listing.bids.all().exists():
        if (
            bid < listing.bids.all().order_by("-bid")[0].bid
            or bid == listing.bids.all().order_by("-bid")[0].bid
        ):
            messages.error(
                request,
                "Bid must be greater than current bid.",
            )
            return HttpResponseRedirect(
                reverse(
                    "listing",
                    args=(listing_id,),
                )
            )
    bid = Bid(bid=bid, listing=listing, user=request.user)
    bid.save()
    messages.success(
        request,
        "Bid added successfully.",
    )
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url=login_url)
def add_comment(request, listing_id):
    """
    Adds a comment to the listing.

    :param request: HTTP request
    :param listing_id: listing id
    :return: listing page
    """

    listing = Listing.objects.get(pk=listing_id)
    comment = Comment(
        comment=request.POST["comment"], listing=listing, user=request.user
    )
    comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url=login_url)
def close_listing(request, listing_id):
    """
    Closes the listing.

    :param request: HTTP request
    :param listing_id: listing id
    :return: listing page
    """

    listing = Listing.objects.get(pk=listing_id)
    if request.user == listing.user:
        listing.close_listing()
        messages.success(
            request,
            "Listing closed.",
        )
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        return HttpResponse("You are not authorized to close this listing.")


@login_required(login_url=login_url)
def user_listings_view(request, username):
    """
    Returns the user page with all the listings of the user.

    :param request: HTTP request
    :param username: username
    :return: user page
    """

    user = User.objects.get(username=username)
    listings = Listing.objects.filter(user=user)
    listing_filter = request.GET.get("filter", "active")
    query = request.GET.get("q", "")
    listings = filter_objects(request, listings, listing_filter, query)
    return render(
        request,
        "auctions/user.html",
        {
            "listings": listings,
            "filter": listing_filter,
            "query": query,
            "page_user": user,
        },
    )
