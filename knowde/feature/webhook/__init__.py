"""ウェブフック."""

from enum import Enum

from pydantic import BaseModel


class ClerkEventType(Enum):
    """Webhook sent event."""

    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELTETED = "user.deleted"
    EMAIL_CREATED = "email.created"


class ClerkPayload(BaseModel, frozen=True):
    """webhook request json."""

    data: dict
    type: ClerkEventType

    @property
    def user_id(self) -> str:  # noqa: D102
        return self.data["id"]

    @property
    def email(self) -> str | None:  # noqa: D102
        if self.type == ClerkEventType.EMAIL_CREATED:
            return self.data["to_email_address"]
        if self.type == ClerkEventType.USER_DELTETED:
            return None
        return self.data["email_addresses"][0]["email_address"]

    @property
    def username(self) -> str | None:  # noqa: D102
        return self.data.get("username")

    def for_register_dict(self) -> dict[str, str | None]:
        """For user sync on webhook."""
        return {
            "email": self.email,
            "clerk_id": self.user_id,
            # clerk由来で作成したユーザーのパスワードは再設定しなければならない
            "hashed_password": "dummy",
            "display_name": self.username,
        }

    def for_update_dict(self) -> dict[str, str]:  # noqa: D102
        d = self.for_register_dict()
        return {
            k: v
            for (
                k,
                v,
            ) in d.items()
            if v != "dummy" and v is not None
        }
