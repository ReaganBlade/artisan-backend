import enum


class UserRole(str, enum.Enum):
    """Platform roles assignable to a user."""

    CUSTOMER = "CUSTOMER"
    ARTIST = "ARTIST"
    ADMIN = "ADMIN"
