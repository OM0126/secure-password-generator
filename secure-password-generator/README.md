# SecureKey - Advanced Password Generator with 2FA

SecureKey is a modern, responsive, and cryptographically secure Password Generator web application built using Django. It features user registration, credential login, a two-factor authentication (2FA) flow sending One-Time Passwords (OTP) to the user's email, real-time entropy calculation, strength meter visualization, session-based password history, interactive dashboards, and light/dark theme switching.

---

## Key Features

1. **User Authentication & Route Protection**: The password generator is protected; users must register and log in to generate passwords.
2. **Two-Factor OTP Security**: Verification code is generated and dispatched to the user's email address upon credentials submission. Valid for 5 minutes.
3. **Cryptographically Secure Generation**: Uses Python's standard `secrets` module to generate passwords, ensuring high randomness suitable for managing secrets.
4. **Entropy Analysis**: Calculates password entropy in bits using the Shannon entropy formula ($H = L \log_2(R)$) based on character pool distribution.
5. **Interactive Strength Meter**: Displays real-time visual progress bars corresponding to password strength classifications (Weak, Medium, Strong, Very Strong).
6. **Session-based Tracking**: Stores up to 10 recently generated passwords within the Django session, offering instant copying options.
7. **Real-time Statistics**: Shows overall statistics (total generated, average entropy, and strength distribution) of the current user session.
8. **No-Reload Experience (AJAX)**: Operations like generation and clearing history are done via asynchronous client-side API requests to Django endpoints, creating a smooth single-page-like experience.
9. **Responsive UI & Dark Mode**: Built with Bootstrap 5 and customized style rules. Includes a light/dark mode switch that remembers the preference via browser `localStorage`.
10. **Unit Tests**: Full unit test coverage for views, forms, authentication flows, and generation constraints.

---

## Folder Structure

```text
secure-password-generator/
│
├── manage.py                          # Django management command line tool
├── requirements.txt                   # Dependency list
├── db.sqlite3                         # SQLite database file
├── README.md                          # Documentation
│
├── secure_password_generator/         # Root project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # Main settings (redirection & emails)
│   ├── urls.py                        # Root URL routing configuration
│   └── wsgi.py
│
└── password_generator/                # App directory
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py                       # Inputs validation (gen, register, login, OTP)
    ├── models.py                      # UserOTP model definition
    ├── tests.py                       # Expanded unit test suite
    ├── urls.py                        # App-specific URL routes
    ├── utils.py                       # Secure generator and entropy analyzer
    ├── views.py                       # Views (Register, Login, OTP verification, Logout)
    │
    ├── static/                        # App static assets
    │   └── password_generator/
    │       ├── css/
    │       │   └── style.css          # Custom styling and transitions
    │       └── js/
    │           └── script.js          # Dynamic AJAX operations & theme toggle
    │
    └── templates/                     # HTML templates
        └── password_generator/
            ├── base.html              # HTML base structure & dynamic navbar
            ├── index.html             # Dashboard and user controls
            ├── register.html          # Registration form
            ├── login.html             # Account login form
            └── verify_otp.html        # 6-Digit OTP entry form
```

---

## Installation & Setup Instructions

### Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### Steps

1. **Clone or Navigate to the Directory**:
   ```bash
   cd secure-password-generator
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Perform Database Migrations**:
   Django uses SQLite by default to store user sessions and OTP profile records:
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:
   - Open your browser and navigate to `http://127.0.0.1:8000/`.
   - You will be redirected to the **Log In** page.
   - Click **Register** to create a user account.
   - Log in using your registered credentials.
   - **Important for Development**: The OTP code will be sent to the email console backend. Check your running server terminal output to find the printed email with your 6-digit OTP code!
   - Paste the code into the verification page to enter the app.

---

## Running Unit Tests

To run the unit tests and verify application constraints:
```bash
python manage.py test
```

---

## Technical Design & Security Analysis

### Password Generation Logic
Unlike Python's standard `random` module, which is pseudo-random and not secure for cryptography, SecureKey utilizes the **`secrets`** module introduced in Python 3.6. It leverages the OS-provided source of randomness (like `/dev/urandom` on Unix systems) to generate cryptographically secure values.
Furthermore, the generator guarantees that at least one character from each checked pool is present in the final password. The character arrays are dynamically shuffled using `secrets.SystemRandom().shuffle` to prevent predictable positioning.

### Shannon Entropy Calculation
Entropy is computed using:
$$H = L \log_2(R)$$
Where:
- $L$ is the password length.
- $R$ is the size of the character pool based on character types actually present in the password:
  - Uppercase letters present: $+26$ to the pool.
  - Lowercase letters present: $+26$ to the pool.
  - Numbers present: $+10$ to the pool.
  - Special characters present: $+32$ to the pool.

Classification levels:
- **Weak**: $< 40$ bits of entropy.
- **Medium**: $40 \le H < 60$ bits.
- **Strong**: $60 \le H < 80$ bits.
- **Very Strong**: $\ge 80$ bits.
