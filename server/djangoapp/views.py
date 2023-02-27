from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel, CarDealer, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_request, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from django.views.decorators.csrf import csrf_exempt

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render all reviews
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = (f"https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/review.json?dealerId={dealer_id}")
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url)
        # Concat all reviews
        review_list = ' '.join([review.sentiment for review in reviews])
        # Return a list of dealer short name
        return HttpResponse(review_list)

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request, dealer_id):
#    if request.user.is_authenticated:
    if request.method == "POST":
        review = {
            "id": 1834,
            "name": "John Smith",
            "dealership": 15,
            "review": "Not happy with this dealership, poor attention",
            "purchase": "false"
        }

        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/post-review.json"
        json_payload = {"review": review}

        # Performing a POST request with the review
        result = post_request(url, json_payload, dealerId=dealer_id)
        if int(result.status_code) == 200:
            print("Review posted successfully.")
#    else:
#        return redirect("/djangoapp/login/")
