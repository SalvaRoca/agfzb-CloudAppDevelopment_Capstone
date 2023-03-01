from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel, CarDealer, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id, get_request, post_request
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
        context = {}
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/dealership.json"
        # Get dealers from the URL
        context["dealerships"] = get_dealers_from_cf(url)
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render all reviews
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = ("https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/dealership.json")
        dealer_obj = get_dealer_by_id(dealer_url, dealer_id)
        if dealer_obj:
            review_url = ("https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/review.json")
            reviews = get_dealer_reviews_from_cf(review_url, dealer_id)
            if reviews:
                dealer_name = dealer_obj.full_name
                context = {
                    "reviews":  reviews, 
                    "dealer_name": dealer_name,
                    "dealer_id": dealer_id
                }
            else: 
                dealer_name = dealer_obj.full_name
                context = {
                    "dealer_name": dealer_name,
                    "dealer_id": dealer_id
                }
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            url = ("https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/dealership.json")
            dealer_obj = get_dealer_by_id(url, dealer_id)
            if dealer_obj:
                dealer_name = dealer_obj.full_name
                context = {
                    "dealer_name": dealer_name,
                    "dealer_id": dealer_id, 
                    "cars": CarModel.objects.all()
                }
            return render(request, 'djangoapp/add_review.html', context)
        if request.method == "POST":
            form = request.POST
            review = dict()
            review["name"] = f"{request.user.first_name} {request.user.last_name}"
            review["dealership"] = dealer_id
            review["review"] = form["content"]
            if form.get("purchasecheck") == "on":
                review["purchase"] = True
            else:
                review["purchase"] = False

            if review["purchase"]:
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%d/%m/%Y").isoformat()
                car = CarModel.objects.get(pk=form["car"])
                review["car_make"] = car.model.name
                review["car_model"] = car.name
                review["car_year"] = car.year
            print (review)
            url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/e6ac8900-a501-4f15-9139-2d3ab04b9289/dealership-package/post-review.json"
            json_payload = {"review": review}

            # Performing a POST request with the review
            result = post_request(url, json_payload, dealerId=dealer_id)
            if result:
                print("Review posted successfully.")
            else:
                print("An error occurred while posting the review, please try again.")
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return redirect("/djangoapp/login/")
