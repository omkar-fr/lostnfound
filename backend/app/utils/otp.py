import secrets

def generate_otp() -> str:
    return "".join([secrets.choice("0123456789") for _ in range(6)])