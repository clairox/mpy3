import random
import string


def generate_id() -> str:
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(10)]
    )
