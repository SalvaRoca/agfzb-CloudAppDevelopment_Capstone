import requests
import json
import os
from .models import CarMake, CarModel, CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


def get_request(url, api_key=False, **kwargs):
    print(f"GET from {url}")
    if api_key:
        # Basic authentication GET
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        except:
            print("An error occurred while making GET request. ")
    else:
        # No authentication GET
        try:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        except:
            print("An error occurred while making GET request. ")

    # Retrieving the response status code and content
    status_code = response.status_code
    print(f"With status {status_code}")
    json_data = json.loads(response.text)

    return json_data


def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        response = None
    return response

    

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


def get_dealer_by_id(url, dealer_id):
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if len(json_result["docs"]) == 1:
        # Get the first (and only) item in the list
        dealer_doc = json_result["docs"][0]
        # Create a CarDealer object with values in `dealer_doc` dictionary
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                short_name=dealer_doc["short_name"],
                                st=dealer_doc["st"], zip=dealer_doc["zip"])
        return dealer_obj
    else:
        return None
    

def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if json_result["docs"]:
        # Get the row list in JSON as dealers
        reviews = json_result["docs"]
        # For each review object
        for review in reviews:
            # Create a DealerReview object with values in `doc` object
            if review["purchase"]:
                review_obj = DealerReview(car_make=review["car_make"], car_model=review["car_model"], car_year=review["car_year"],
                                          dealership=review["dealership"], id=review["_id"], name=review["name"],
                                          purchase=review["purchase"], purchase_date=review["purchase_date"], review=review["review"])
            else:
                review_obj = DealerReview(dealership=review["dealership"], id=review["_id"], name=review["name"],
                                          purchase=review["purchase"], review=review["review"])
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            results.append(review_obj)

    return results


def analyze_review_sentiments(review):
    url = 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/94cc1476-9bbf-49f3-95fc-124de6cd3072'
    api_key = '0odmxMyFdLdpwNzCDMVUvqA6nOCkyDHPGQw5mROu2tDm'

    version = '2021-08-01'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)

    try:
        response = nlu.analyze(text=review, features=Features(
            sentiment=SentimentOptions())).get_result()
        print(json.dumps(response))
        sentiment_score = str(response["sentiment"]["document"]["score"])
        print(sentiment_score)
        sentiment_label = response["sentiment"]["document"]["label"]
    except:
        print("Review is too short for sentiment analysis. Assigning default sentiment value 'neutral' instead")
        sentiment_label = "neutral"

    print(sentiment_label)

    return sentiment_label
