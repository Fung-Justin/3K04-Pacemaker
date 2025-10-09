import json, os, hashlib, secrets
from dataclasses import dataclass

USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "users.json")

@dataclass
class User:
    username_hash: str
    pw_hash: str
    salt_user: str
    salt_pw: str


def _hash_with_salt(value: str, salt_hex: str) -> str:
    """Hash any string value using SHA-256 and a provided salt."""
    salt = bytes.fromhex(salt_hex)
    return hashlib.sha256(salt + value.encode("utf-8")).hexdigest()


class UserStore:
    """Local JSON user system with hashed usernames and passwords."""

    def __init__(self, path: str = USERS_PATH, max_users: int = 10):
        self.path = os.path.abspath(path)
        self.max_users = max_users
        self._users = []  # list of User objects
        self._load()

    # ---------- internal IO ----------
    def _load(self):
        if not os.path.exists(self.path):
            self._save()
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._users = [User(**u) for u in data.get("users", [])]
        except Exception:
            self._users = []

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"users": [u.__dict__ for u in self._users]}, f, indent=2)

    # ---------- helpers ----------
    def _find_user(self, username: str):
        """Return the user that matches a given plaintext username."""
        for u in self._users:
            # recompute hash and compare
            user_hash_try = _hash_with_salt(username, u.salt_user)
            if user_hash_try == u.username_hash:
                return u
        return None

    # ---------- public ----------
    def count(self): return len(self._users)

    def register(self, username: str, password: str):
        username = username.strip()
        if not username or not password:
            return False, "Username and password are required."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        if self._find_user(username):
            return False, "That username is already taken."
        if self.count() >= self.max_users:
            return False, f"User limit reached ({self.max_users})."

        # independent salts for username and password
        salt_user = secrets.token_hex(16)
        salt_pw = secrets.token_hex(16)

        username_hash = _hash_with_salt(username, salt_user)
        pw_hash = _hash_with_salt(password, salt_pw)

        self._users.append(User(username_hash, pw_hash, salt_user, salt_pw))
        self._save()
        return True, "Account created successfully."

    def check_credentials(self, username: str, password: str) -> bool:
        u = self._find_user(username)
        if not u:
            return False
        return _hash_with_salt(password, u.salt_pw) == u.pw_hash
