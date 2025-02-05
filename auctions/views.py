from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import ListingCategory, User, Listing, Bid, Comment, Watcher
from django.contrib.auth.decorators import login_required


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })



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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required    
def bid_add(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        amount = request.POST["amount"]
        user = request.user

        if float(amount) <= listing.current_bid or float(amount) <= listing.starting_bid:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Your bid must be greater than the current bid."
            })
        
        # Add new bid
        Bid.objects.create(
            listing=listing,
            bidder=user,
            amount=amount
        )

        # Update current bid for this listing
        listing.current_bid = amount
        listing.current_bidder = user
        listing.save()


        return HttpResponseRedirect(reverse("listing", args=(listing_id,))) 

@login_required
def categories(request):
    categories = ListingCategory.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def category(request, category_id):
    category = ListingCategory.objects.get(id=category_id)
    listings = Listing.objects.filter(category=category ,is_active=True)
    return render(request, "auctions/index.html", {
        "category": category,
        "listings": listings
    })

@login_required
def closed(request):
    closed_listings = Listing.objects.filter(is_active=False)
    return render(request, "auctions/closed.html", {
        "listings": closed_listings
    })

@login_required
def comment_add(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        content = request.POST["content"]
        user = request.user

        # Add new comment
        Comment.objects.create(
            listing=listing,
            user=user,
            content=content
        )

        return HttpResponseRedirect(reverse("listing", args=(listing_id,))) 


@login_required
def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bids = listing.bids.all()
    comments = listing.comments.all()
    user = request.user
    is_watched = Watcher.objects.filter(user=user, listing=listing).exists()
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "is_watched": is_watched
    })

@login_required
def listing_add(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category = ListingCategory.objects.get(id = request.POST["category"])
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        user = request.user

        if not user.is_authenticated:
            return HttpResponseRedirect(request, "auctions/index.html", {
                "message": "You must be logged in to add a listing."
            })
        
        Listing.objects.create(
            create_user=user,
            title=title,
            description=description,
            category=category,
            image_url=image_url,
            starting_bid=starting_bid,
            current_bid=0,
            current_bidder=None,
        )

        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/listing_add.html", {
        "categories": ListingCategory.objects.all()
    })

@login_required    
def listing_close(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if listing.create_user != request.user:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "message": "You are not the owner of this listing."
        })
    
    listing.is_active = False
    listing.save()
    return HttpResponseRedirect(reverse("index"))

@login_required
def watchlist(request):
    user = request.user
    watchers = Watcher.objects.filter(user=user)
    watched_listings = [watcher.listing for watcher in watchers]
    return render(request, "auctions/index.html", {
        "watchlist": True,
        "listings": watched_listings
    })

@login_required
def watch_toggle(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user

    if Watcher.objects.filter(user=user, listing=listing).exists():
        Watcher.objects.filter(user=user, listing=listing).delete()
    else:
        Watcher.objects.create(
            user=user,
            listing=listing
        )

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))  
