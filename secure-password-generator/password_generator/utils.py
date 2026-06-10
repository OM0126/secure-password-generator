import math
import secrets
import string

def generate_secure_password(length, use_upper, use_lower, use_digits, use_special):
    """
    Generates a secure password using the secrets module.
    Guarantees at least one character from each selected pool is present.
    """
    pools = []
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_digits:
        pools.append(string.digits)
    if use_special:
        # A clean, common set of special characters to avoid escaping issues
        pools.append("!@#$%^&*()_+-=[]{}|;:,.<>?")

    if not pools:
        raise ValueError("At least one character type must be selected.")

    if length < 8 or length > 50:
        raise ValueError("Password length must be between 8 and 50 characters.")

    password_chars = []
    
    # 1. Guarantee at least one character from each selected category
    for pool in pools:
        password_chars.append(secrets.choice(pool))

    # 2. Fill the rest of the password length with random characters from the combined pool
    combined_pool = "".join(pools)
    while len(password_chars) < length:
        password_chars.append(secrets.choice(combined_pool))

    # 3. Securely shuffle the password characters
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def analyze_password_strength(password):
    """
    Analyzes the password and calculates Shannon entropy.
    Returns a dictionary with entropy value, strength classification, and feedback.
    """
    if not password:
        return {
            "entropy": 0.0,
            "strength": "None",
            "color": "secondary",
            "progress": 0,
            "feedback": "No password provided."
        }

    length = len(password)
    
    # Check what character sets are present in the password
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    # Determine size of pool (R) based on types of characters detected
    pool_size = 0
    if has_lower:
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_digits:
        pool_size += 10
    if has_special:
        pool_size += 32 # Approximate size of standard punctuation set

    if pool_size == 0:
        return {
            "entropy": 0.0,
            "strength": "Weak",
            "color": "danger",
            "progress": 10,
            "feedback": "Password consists of invalid characters."
        }

    # Shannon Entropy formula: H = L * log2(R)
    entropy = length * math.log2(pool_size)
    entropy = round(entropy, 1)

    # Classify strength based on entropy levels
    if entropy < 40:
        strength = "Weak"
        color = "danger"
        progress = 25
        feedback = "Weak protection. Increase length or include more character types."
    elif entropy < 60:
        strength = "Medium"
        color = "warning"
        progress = 50
        feedback = "Moderate protection. Try extending length to 12+ characters."
    elif entropy < 80:
        strength = "Strong"
        color = "success"
        progress = 75
        feedback = "Strong protection! Suitable for personal accounts."
    else:
        strength = "Very Strong"
        color = "info" # Bootstrap info (cyan/teal) or custom styles will make it pop
        progress = 100
        feedback = "Highly secure. Excellent protection against brute-force attacks!"

    return {
        "entropy": entropy,
        "strength": strength,
        "color": color,
        "progress": progress,
        "feedback": feedback,
        "pool_size": pool_size
    }
