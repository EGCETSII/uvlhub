from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

ROLES = ["admin", "curator", "standard", "guest"]
DEFAULT_ROLE = "standard"



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    # Two-factor auth fields (TOTP)
    totp_secret = db.Column(db.String(64), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    role = db.Column(db.String(20), nullable=False, default=DEFAULT_ROLE)

    data_sets = db.relationship("DataSet", backref="user", lazy=True)
    profile = db.relationship("UserProfile", backref="user", uselist=False)

    def init(self, kwargs):
        super(User, self).init(kwargs)
        if "password" in kwargs:
            self.set_password(kwargs["password"])

    def repr(self):
        return f"<User {self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def temp_folder(self) -> str:
        from app.modules.auth.services import AuthenticationService

        return AuthenticationService().temp_folder_by_user(self)

    def verify_totp(self, token: str) -> bool:
        """Verify a TOTP token using the user's secret. Returns True if valid."""
        if not self.totp_secret:
            return False
        try:
            import pyotp

            totp = pyotp.TOTP(self.totp_secret)
            return totp.verify(token, valid_window=1)
        except Exception:
            return False
        
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
