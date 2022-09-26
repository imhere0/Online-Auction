from django.shortcuts import render
from .models import User, Listing, BidModel, Winner, CommentModel
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect 
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import make_password, check_password
import re

# Registering the User.
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Validating Email.
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if(not re.fullmatch(regex, email)):
            return render(request, "sale/register.html", {
                "message": "Email must be a valid email."
            })

        if password != confirmation:
            return render(request, "sale/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

        except IntegrityError:
            return render(request, "sale/register.html", {
                "message": "Username already taken."
            })
        return render(request, "sale/login.html")
    else:
        return render(request, "sale/register.html")

@csrf_protect
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
            return render(request, "sale/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "sale/login.html")


def index(request):

    winner_list = []
    posts = []

    try:
        winnerobject0 = Winner.objects.all()
    except:
        winnerobject0 = None

    if winnerobject0:
        
        for element in winnerobject0:
            winner_list.append(element.id)

        listingobj0 = Listing.objects.all()
        
        for item in listingobj0:
            if item.id not in winner_list:
                posts.append(item)

        return render(request, "sale/index.html", {
            "posts": posts
        })

    listingobj1 = Listing.objects.all()
    return render(request, "sale/index.html", {
        "posts": listingobj1
    })


@login_required
@csrf_protect
def create_listing(request):
    if request.method == "POST":

        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]


        # Checking the presence of mandatory fields.
        if not title or not description or not price :
            return render(request, "sale/create_listing.html", {
                "message" : " Mandotary Form Field must be provided."
            })

        
        image = request.FILES['image']
        current_user = request.user

        # Creating the listing Object.
        listingobj = Listing.objects.create(title = title, description = description, price = price, image = image, owner = current_user.username, owner_id = current_user)
        listingobj.save()

        all_objects = Listing.objects.all()

        return redirect('index')
    else:
        # Rendering the page for listing creation.
        return render(request, "sale/create_listing.html")




def title(request, id):
    
    listingobject = Listing.objects.get(id = id)

    current_user = request.user       


    if request.method == "POST":
        
        try:
            bid = request.POST["bid"]
        except:
            bid = None

        if bid:
            if int(bid) <= int(listingobject.price):
                raise PermissionDenied("The Bid must be greater then the current price of the associated object")
            try:    
                biddingobject = BidModel.objects.get(listingid = id)
            except:
                biddingobject = None

            if biddingobject:
                biddingobject.delete()

            biddingobject1 = BidModel.objects.create(listingid = listingobject, user_id = current_user, amount = bid)
            biddingobject1.save()
            

            listingobject.price = bid
            listingobject.save()

        try:
            comment = request.POST["comment"]
        except:
            comment = None

        if comment:
            commentobject = CommentModel.objects.create(user_id = current_user, listingid = listingobject, comment = comment)
            commentobject.save()
        
        try:
            close_bid = request.POST["bidclose"]
        except:
            close_bid = None

        if close_bid:

            try:
                biddingobject1 = BidModel.objects.get(listingid = listingobject)
            except:
                biddingobject1 = None

            

            if biddingobject1:
                bid_winner = biddingobject1.user_id.username

                winnerobject = Winner.objects.create(price = listingobject.price, listingid = listingobject, winner = bid_winner, owner = listingobject.owner)
                winnerobject.save()                                

        return HttpResponseRedirect(reverse("title", args = (id,)))

    else:
        try:
            commentobject1 = CommentModel.objects.filter(listingid = listingobject)
        except:
            commentobject1 = None

    try:        
        biddingobject2 = BidModel.objects.get(listingid = listingobject)
    except:
        biddingobject2 = None
    bid_message = "This is bid message"            

    try:
        winnerobject1 = Winner.objects.get(listingid = listingobject)

    except:
        winnerobject1 = None

    if winnerobject1:
        return render(request, "sale/title.html",{
            "post":listingobject,"id":id,"winner":winnerobject1,"comments":commentobject1
        })

                        
    return render(request, "sale/title.html",{
        "post":listingobject,"id":id,"comments":commentobject1,"bids":biddingobject2,"bid_message":bid_message
    })
        

def closed_listing(request):
    winner_list = []
    posts = []

    try:
        winnerobject0 = Winner.objects.all()
    except:
        winnerobject0 = None

    if winnerobject0:
        
        for element in winnerobject0:
            winner_list.append(element.id)

        listingobj0 = Listing.objects.all()

        for item in listingobj0:
            if item.id in winner_list:
                posts.append(item)

        return render(request, "sale/closed_listing.html", {
            "posts": posts
        })
    else:
        return render(request, "sale/closed_listing.html",{
            "message":"No listing has been closed"
        })


@login_required
def remove(request, id):
            

        listingobject1 = Listing.objects.get(id = id)
        listingobject1.delete()
        return render(request, "sale/index.html",{
            "posts": Listing.objects.all()
        })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))