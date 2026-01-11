import random

def generate_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    return {
        "question": f"{a} + {b}",
        "answer": str(a + b),
    }
