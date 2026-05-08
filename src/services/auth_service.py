import csv
import os


class AuthService:
    def __init__(self, users_csv_path=None):
        if users_csv_path is None:
            self.users_csv_path = os.path.join("src", "data", "users.csv")
        else:
            self.users_csv_path = users_csv_path

    def authenticate(self, username, password):
        if not os.path.exists(self.users_csv_path):
            return None

        with open(self.users_csv_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("username") == username and row.get("password") == password:
                    return {
                        "user_id": row.get("user_id", ""),
                        "username": row.get("username", ""),
                        "role": row.get("role", "user"),
                    }

        return None
