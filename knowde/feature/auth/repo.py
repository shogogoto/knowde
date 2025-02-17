"""DB."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from fastapi_users.db import (
    BaseUserDatabase,
)

from knowde.primitive.account import User
from knowde.primitive.account.repo import LAccount

if TYPE_CHECKING:
    from fastapi_users.models import OAP, UOAP


class AccountDB(BaseUserDatabase[User, UUID]):
    """DB adapter for fastapi-users."""

    async def get(self, id: UUID) -> User | None:  # noqa: A002
        """Get a single user by id."""
        # print("---------get")
        lb = LAccount.nodes.get_or_none(uid=id.hex)
        return None if lb is None else User.from_lb(lb)

    async def get_by_email(self, email: str) -> User | None:
        """Get a single user by email."""
        # print("---------get by email")
        lb = LAccount.nodes.get_or_none(email=email)
        return None if lb is None else User.from_lb(lb)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> User | None:
        """Get a single user by OAuth account id."""
        # print("---------get by oauth")
        lb = LAccount.nodes.get_or_none(oauth_name=oauth, account_id=account_id)
        return User.from_lb(lb)

    async def create(self, create_dict: dict[str, Any]) -> User:
        """Create a user."""
        # print("------------ create")
        lb = LAccount(**create_dict).save()
        return User.from_lb(lb)

    async def update(self, user: User, update_dict: dict) -> User:
        """Update a user."""
        # print("------------ update")
        lb = LAccount.nodes.get(uid=user.id.hex)
        for key, value in update_dict.items():
            if value is None:
                continue
            setattr(lb, key, value)
        lb = lb.save()
        return User.from_lb(lb)

    async def delete(self, user: User) -> None:
        """Delete a user."""
        # print("------------ delete")
        lb = LAccount.nodes.get(uid=user.id.hex)
        await lb.delete()

    ########################################################### OAUTH
    async def add_oauth_account(
        self: BaseUserDatabase,
        user: UOAP,
        create_dict: dict[str, Any],
    ) -> UOAP:
        """Create an OAuth account and add it to the user."""
        # print("------------ add oauth account")

    async def update_oauth_account(
        self: BaseUserDatabase,
        user: UOAP,
        oauth_account: OAP,
        update_dict: dict[str, Any],
    ) -> UOAP:
        """Update an OAuth account on a user."""
        # print("------------ update oauth account")


# class Base(DeclarativeBase):
#     pass


# class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
#     pass


# class User(SQLAlchemyBaseUserTableUUID, Base):
#     oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
#         "OAuthAccount",
#         lazy="joined",
#     )


# engine = create_async_engine(DATABASE_URL)
# async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# async def create_db_and_tables() -> None:
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session


# async def get_user_db(session: AsyncSession = Depends(get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User, OAuthAccount)
