import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)

class ListingCategory(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):

    create_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.ForeignKey(ListingCategory, on_delete=models.DO_NOTHING, related_name="listings")
    image_url = models.URLField(max_length=200)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bidder = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="leading_bids", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}: {self.title} to {self.category}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    create_date = models.DateTimeField("Bid Date", auto_now=False, auto_now_add=True)

    def __str__(self):
        return f"{self.bidder}: {self.amount}"
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    create_date = models.DateTimeField("Bid Date", auto_now=False, auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.content}"

class Watcher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchers")
    
    def __str__(self):
        return f"{self.listing}"
