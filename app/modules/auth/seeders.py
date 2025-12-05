from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from core.seeders.BaseSeeder import BaseSeeder


class AuthSeeder(BaseSeeder):

    priority = 1  # Higher priority

    def run(self):

        # Seeding users
        # Create User instances and ensure passwords are hashed via `set_password`
        raw_users = [
            ("user1@example.com", "1234"),
            ("user2@example.com", "1234"),
        ]

        users = []
        for email, plain_pw in raw_users:
            u = User(email=email)
            # Use model helper to set a proper hash instead of storing plaintext
            u.set_password(plain_pw)
            users.append(u)

        # Inserted users with their assigned IDs are returned by `self.seed`.
        seeded_users = self.seed(users)

        # Create profiles for each user inserted.
        user_profiles = []
        names = [("John", "Doe"), ("Jane", "Doe")]

        for user, name in zip(seeded_users, names):
            profile_data = {
                "user_id": user.id,
                "orcid": "",
                "affiliation": "Some University",
                "name": name[0],
                "surname": name[1],
            }
            user_profile = UserProfile(**profile_data)
            user_profiles.append(user_profile)

        # Seeding user profiles
        self.seed(user_profiles)
