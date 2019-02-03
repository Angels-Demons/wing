from decimal import Decimal

# from .models import Scooter


# def nearby_devices(latitude, longitude, radius):
#     scooters = Scooter.objects.all()
#     nearby = []
#     for scooter in scooters:
#         if abs((scooter.latitude + scooter.longitude) - (Decimal(latitude) + Decimal(longitude))) < 2*Decimal(radius):
#             nearby.append(scooter)
#     return nearby


def price(ride):
    return 1500
