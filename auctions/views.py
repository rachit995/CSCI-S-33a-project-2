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
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
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
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
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
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        category = Category.objects.get(category=request.POST["category"])

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
            return render(request, "auctions/create.html")
        return HttpResponseRedirect(reverse("index"))
    return render(
        request, "auctions/create.html", {"categories": Category.objects.all()}
    )


def listing(request, listing_id, error_message=""):
    listing = Listing.objects.get(pk=listing_id)
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "bids": listing.bids.all(),
            "comments": listing.get_comments(),
        },
    )


@login_required(login_url=login_url)
def watchlist(request):
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


def categories(request):
    categories = Category.objects.all()
    return render(
        request, "auctions/categories.html", {"categories": categories}
    )


def category(request, category):
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
    listing = Listing.objects.get(pk=listing_id)
    comment = Comment(
        comment=request.POST["comment"], listing=listing, user=request.user
    )
    comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url=login_url)
def close_listing(request, listing_id):
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
def user(request, username):
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
        },
    )
