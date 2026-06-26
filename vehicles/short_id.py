from nanoid import generate

SHORT_ID_SIZE = 12
SHORT_ID_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_vehicle_short_id() -> str:
    from vehicles.models import Vehicle

    for _ in range(10):
        candidate = generate(SHORT_ID_ALPHABET, SHORT_ID_SIZE)
        if not Vehicle.objects.filter(short_id=candidate).exists():
            return candidate
    raise RuntimeError("Could not generate a unique vehicle short_id")
