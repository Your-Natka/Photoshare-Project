"""
messages.py — константи для повідомлень у PhotoShare API

Цей файл містить усі тексти повідомлень, які повертає API
для користувачів та адміністрації.
Використовується для централізованого управління повідомленнями.
"""

# -------------------- WELCOME --------------------
WELCOME_MESSAGE = "Welcome to Photoshare!"

# -------------------- DATABASE --------------------
DB_CONFIG_ERROR = "Database is not configured correctly"
DB_CONNECT_ERROR = "Error connecting to the database"

# -------------------- USER / ACCOUNT --------------------
NOT_FOUND = 'Not Found'
ALREADY_EXISTS = "Account already exists"
DOESNT_EXISTS = "Account doesn't exists"
SUCCESS_CREATE_USER = "User successfully created. Check your email for confirmation."
INVALID_PASSWORD = "Invalid password"
INVALID_TOKEN = "Invalid refresh token"
VERIFICATION_ERROR = "Verification error"
INVALID_EMAIL = "Invalid email"
EMAIL_NOT_CONFIRMED = "Email not confirmed"
EMAIL_ALREADY_CONFIRMED = "Your email is already confirmed"
EMAIL_CONFIRMED = "Email successfully confirmed"
EMAIL_HAS_BEEN_SEND = "Email has been send"
CHECK_YOUR_EMAIL = "Check your email for confirmation."
FAIL_EMAIL_VERIFICATION = "Invalid token for email verification"
INVALID_SCOPE = 'Invalid scope for token'
NOT_VALIDATE_CREDENTIALS = 'Could not validate credentials'

USER_NOT_ACTIVE = "User is banned"
USER_ALREADY_NOT_ACTIVE = "User already is banned"
USER_IS_LOGOUT = "Successfully logged out!"
USER_ROLE_EXISTS = "Role is already exists"
USER_CHANGE_ROLE_TO = "User role changed to"

# -------------------- REQUESTS / RATE LIMIT --------------------
TOO_MANY_REQUESTS = 'No more than 10 requests per minute'

# -------------------- POSTS --------------------
INVALID_URL = "Invalid url"
TOO_MANY_HASHTAGS = "Too many hashtags! Maximum 5."
NO_POST_ID = "No post with this ID."
OWN_POST = "It`s not possible vote for own post."

# -------------------- COMMENTS --------------------
COMM_NOT_FOUND = "Comment not found or not available."

# -------------------- RATINGS --------------------
NO_RATING = "Rating not found or not available."
VOTE_TWICE = "It`s not possible to vote twice."

# -------------------- PERMISSIONS --------------------
OPERATION_FORBIDDEN = "Operation forbidden"
