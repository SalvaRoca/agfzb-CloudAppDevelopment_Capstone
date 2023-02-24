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
    year = models.DateField(default=now)

    def __str__(self):
        return str(self.model) + \
            self.name + "," + \
            self.cartype


# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
