import random

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

def generate_hint(number, range_top):
    """
    Returns a random mathematical hint about the number.
    """
    options = []

    # 1. Parity
    if number % 2 == 0:
        options.append("The number is Even.")
    else:
        options.append("The number is Odd.")

    # 2. Divisibility (Factors)
    for i in [3, 4, 5, 7, 9, 10]:
        if number % i == 0:
            options.append(f"The number is a multiple of {i}.")
        else:
            # Sometimes knowing what it isn't is helpful too
            # options.append(f"The number is NOT divisible by {i}.")
            pass

    # 3. Prime Check
    if is_prime(number):
        options.append("The number is a Prime number.")
    
    # 4. Digit Sum
    digits = [int(d) for d in str(number)]
    digit_sum = sum(digits)
    options.append(f"The sum of the digits is {digit_sum}.")

    # 5. Range Slicing (Greater/Less than midpoints)
    # We pick a random checkpoint to help them narrow it down
    checkpoint = random.randint(1, range_top)
    if number > checkpoint:
        options.append(f"The number is greater than {checkpoint}.")
    else:
        options.append(f"The number is less than {checkpoint}.")

    # Pick one random hint from the list
    return random.choice(options)