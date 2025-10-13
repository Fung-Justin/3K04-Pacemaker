import json, os, hashlib, secrets # standard libraries
from dataclasses import dataclass # for easy data storage

USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "users.json") # default user file path

@dataclass # simple class to hold user data
class User:
    username_hash: str # hashed username
    pw_hash: str # hashed password
    salt_user: str # salt for username
    salt_pw: str # salt for password


def _hash_with_salt(value: str, salt_hex: str) -> str: # Hash any string value using SHA-256 and a provided salt.
    salt = bytes.fromhex(salt_hex) # convert hex to bytes
    return hashlib.sha256(salt + value.encode("utf-8")).hexdigest() # return hex digest


class UserStore: # Local JSON user system with hashed usernames and passwords.

    def __init__(self, path: str = USERS_PATH, max_users: int = 10): # Initialize the user store
        self.path = os.path.abspath(path) # absolute path to user file
        self.max_users = max_users # maximum number of users
        self._users = []  # list of User objects
        self._load() # load users from file

    def _load(self): # Load users from the JSON file
        if not os.path.exists(self.path): # if file doesn't exist, create it
            self._save() # create empty file
        try: # load existing users
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f) # load JSON data
            self._users = [User(**u) for u in data.get("users", [])] # create User objects
        except Exception: # on error, start fresh
            self._users = [] # empty user list

    def _save(self): # Save users to the JSON file
        os.makedirs(os.path.dirname(self.path), exist_ok=True) # ensure directory exists
        with open(self.path, "w", encoding="utf-8") as f: # write to file
            json.dump({"users": [u.__dict__ for u in self._users]}, f, indent=2) # save user data

    def _find_user(self, username: str): # Return the user that matches a given plaintext username.
        for u in self._users: 
            # recompute hash and compare
            user_hash_try = _hash_with_salt(username, u.salt_user) 
            if user_hash_try == u.username_hash: # match found
                return u 
        return None # no match

    def count(self): return len(self._users) # Return the number of registered users.

    def register(self, username: str, password: str): # Register a new user with username and password.
        username = username.strip() # clean whitespace
        if not username or not password: # both required
            return False, "Username and password are required." 
        if len(username) < 3: # username length check
            return False, "Username must be at least 3 characters."
        if len(password) < 6: # password length check
            return False, "Password must be at least 6 characters."
        if self._find_user(username): # username must be unique
            return False, "That username is already taken."
        if self.count() >= self.max_users: # user limit check
            return False, f"User limit reached ({self.max_users})."

        # independent salts for username and password
        salt_user = secrets.token_hex(16) # 16 bytes = 32 hex chars
        salt_pw = secrets.token_hex(16) # 16 bytes = 32 hex chars

        username_hash = _hash_with_salt(username, salt_user) # hash username
        pw_hash = _hash_with_salt(password, salt_pw) # hash password

        self._users.append(User(username_hash, pw_hash, salt_user, salt_pw)) # add new user
        self._save() # save to file
        return True, "Account created successfully." # success

    def check_credentials(self, username: str, password: str) -> bool: # Verify username and password.
        u = self._find_user(username) # find user by username
        if not u: 
            return False # user not found
        return _hash_with_salt(password, u.salt_pw) == u.pw_hash # verify password hash
