from django.db import models
from django.utils.timezone import now

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30, default='Car Make')
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    SEDAN = 'sedan'
    HATCHBACK = 'hatchback'
    CABRIO = 'cabrio'
    SUV = 'SUV'
    WAGON = 'wagon'
    CAR_TYPES = [   
        (SEDAN, 'Sedan'),
        (HATCHBACK, 'Hatchback'),
        (CABRIO, 'Cabrio'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon')
    ]

    model = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default='Car Name')
    dealerId = models.IntegerField(default=0)
    cartype = models.CharField(max_length=9, choices=CAR_TYPES, default=SEDAN)
    year = models.IntegerField(default=2023)

    def __str__(self):
        return str(self.model) + \
            self.name + "," + \
            self.cartype


class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name


class DealerReview:

    def __init__(self, car_make, car_model, car_year, dealership, id, name, purchase, purchase_date, review):
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.dealership = dealership
        self.id = id
        self.name = name
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.review = review
        #self.sentiment = sentiment

    def __str__(self):
        return "Review: " + self.review

