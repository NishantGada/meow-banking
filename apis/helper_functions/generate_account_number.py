import random
import string


def generate_account_number():
    return "".join(random.choices(string.digits, k=10))
