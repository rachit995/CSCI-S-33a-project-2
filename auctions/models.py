from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"


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
    watchlist = models.ManyToManyField(
        User, blank=True, related_name="watchlist"
    )

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = models.IntegerField()
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids"
    )

    def __str__(self):
        return f"{self.bid}"


class Comment(models.Model):
    comment = models.CharField(max_length=256)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return f"{self.comment}"


class Watchlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlists"
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watchlists"
    )

    def __str__(self):
        return f"{self.user}"
