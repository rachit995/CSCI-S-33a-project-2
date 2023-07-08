from django.contrib import admin

# Register your models here.

from .models import User, Category, Listing, Bid, Comment, Watchlist


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "created_at", "updated_at")


class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "image_url",
        "active",
        "starting_bid",
        "category",
        "created_at",
        "updated_at",
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "comment",
        "listing",
        "user",
        "created_at",
        "updated_at",
    )


class WatchlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "listing",
        "user",
        "created_at",
        "updated_at",
    )


class BidAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "bid",
        "listing",
        "user",
        "created_at",
        "updated_at",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
