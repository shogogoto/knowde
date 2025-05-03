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
        if self.type in {ClerkEventType.EMAIL_CREATED, ClerkEventType.USER_DELTETED}:
            return self.data["to_email_address"]
        if self.type == ClerkEventType.USER_DELTETED:
            return None
        return self.data["email_addresses"][0]["email_address"]
