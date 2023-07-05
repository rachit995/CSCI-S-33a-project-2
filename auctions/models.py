from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.utils import timezone
from .utils import get_time_ago


class User(AbstractUser):
    def __str__(self):
        return f"{self.username.capitalize()}"


class Category(models.Model):
    category = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.capitalize()}"

    def listing_count(self):
        return self.listings.count()


class Listing(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings"
    )
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    image_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    starting_bid = models.IntegerField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="listings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title.capitalize()}"

    def posted_time_ago(self):
        return get_time_ago(self.created_at)

    def get_highest_bid(self):
        return self.bids.order_by("-bid").first()

    def close_listing(self):
        self.active = False
        self.save()
        highest_bid = self.bids.order_by("-bid").first()
        if highest_bid:
            highest_bid.winner = True
            highest_bid.save()

    def get_comments(self):
        return self.comments.order_by("-created_at")

    def get_watchlist_count(self):
        return self.watchlists.count()

    def get_watchlist_users(self):
        return self.watchlists.all().values_list("user", flat=True)

    def winner(self):
        return self.bids.filter(winner=True).first()

    def current_bid(self):
        try:
            return self.bids.order_by("-bid").first().bid
        except AttributeError:
            return self.starting_bid

    def bid_count(self):
        return self.bids.count()

    def is_in_watchlist(self, user):
        return self.watchlists.filter(user=user).exists()


class Bid(models.Model):
    bid = models.IntegerField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids"
    )
    winner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} bid {self.bid} on {self.listing}"


class Comment(models.Model):
    comment = models.CharField(max_length=256)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.comment}"

    def posted_time_ago(self):
        return get_time_ago(self.created_at)


class Watchlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlists"
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watchlists"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}"
