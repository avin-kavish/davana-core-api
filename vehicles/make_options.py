POPULAR_JAPANESE_MAKES = (
    "Daihatsu",
    "Honda",
    "Isuzu",
    "Lexus",
    "Mazda",
    "Mitsubishi",
    "Nissan",
    "Subaru",
    "Suzuki",
    "Toyota",
)

POPULAR_EUROPEAN_MAKES = (
    "Audi",
    "BMW",
    "Citroën",
    "Fiat",
    "Jaguar",
    "Land Rover",
    "Mercedes-Benz",
    "MINI",
    "Opel",
    "Peugeot",
    "Porsche",
    "Renault",
    "SEAT",
    "Skoda",
    "Volkswagen",
    "Volvo",
)

POPULAR_VEHICLE_MAKES = tuple(
    dict.fromkeys(POPULAR_JAPANESE_MAKES + POPULAR_EUROPEAN_MAKES)
)
