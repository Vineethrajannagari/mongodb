"""
Bank account with deposit, withdraw and balance operations, persisted in MongoDB.

Each BankAccount instance belongs to exactly one user: the owner is set at
construction time and cannot be changed afterwards. The balance and the
transaction history live in the `accounts` collection, one document per user,
so two objects created for the same user always see the same money.
"""

import os
from datetime import datetime

from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ConnectionFailure

DEFAULT_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DEFAULT_DB = os.getenv("BANK_DB", "bank")


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""


class BankAccount:
    """A bank account owned by a single user and stored in MongoDB."""

    def __init__(self, user_id, owner_name=None, initial_balance=0.0,
                 connection_string=DEFAULT_URI, database_name=DEFAULT_DB):
        """
        Open (or create) the MongoDB-backed account of a single user.

        Args:
            user_id: Unique identifier of the user owning this account
            owner_name: Display name, required only when creating the account
            initial_balance: Opening balance used only on creation
            connection_string: MongoDB connection URI
            database_name: Database holding the `accounts` collection

        Raises:
            ValueError: If user_id is empty, initial_balance is negative, or
                the account does not exist yet and owner_name is missing
            ConnectionFailure: If unable to connect to MongoDB
        """
        if not user_id:
            raise ValueError("user_id is required")
        if initial_balance < 0:
            raise ValueError("initial_balance cannot be negative")

        try:
            self.client = MongoClient(connection_string)
            self.client.admin.command("ping")
        except ConnectionFailure as e:
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")

        self.accounts = self.client[database_name].accounts
        self.accounts.create_index("user_id", unique=True, name="user_id_unique")

        self._user_id = user_id
        existing = self.accounts.find_one({"user_id": user_id})
        if existing is None:
            if not owner_name:
                raise ValueError(
                    f"owner_name is required to open a new account for {user_id}"
                )
            self.accounts.insert_one({
                "user_id": user_id,
                "owner_name": owner_name,
                "balance": float(initial_balance),
                "transactions": [],
                "created_at": datetime.utcnow(),
            })
            self._owner_name = owner_name
        else:
            self._owner_name = existing["owner_name"]

    @property
    def user_id(self):
        return self._user_id

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def transactions(self):
        """Transaction history of this user, oldest first."""
        doc = self.accounts.find_one({"user_id": self._user_id}, {"transactions": 1})
        return doc["transactions"] if doc else []

    def deposit(self, amount):
        """
        Add money to the account.

        Args:
            amount: Positive amount to deposit

        Returns:
            The new balance

        Raises:
            ValueError: If amount is not positive
        """
        amount = self._validate_amount(amount)
        return self._apply({"user_id": self._user_id}, "deposit", amount)

    def withdraw(self, amount):
        """
        Remove money from the account.

        Args:
            amount: Positive amount to withdraw

        Returns:
            The new balance

        Raises:
            ValueError: If amount is not positive
            InsufficientFundsError: If amount exceeds the current balance
        """
        amount = self._validate_amount(amount)
        try:
            # The balance guard is part of the filter, so a concurrent
            # withdrawal can never push the account below zero.
            return self._apply(
                {"user_id": self._user_id, "balance": {"$gte": amount}},
                "withdraw",
                -amount,
            )
        except LookupError:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount:.2f}: balance is {self.get_balance():.2f}"
            )

    def get_balance(self):
        """Return the current balance stored in MongoDB."""
        doc = self.accounts.find_one({"user_id": self._user_id}, {"balance": 1})
        if doc is None:
            raise LookupError(f"No account found for user {self._user_id}")
        return doc["balance"]

    def _apply(self, query, kind, delta):
        doc = self.accounts.find_one_and_update(
            query,
            {
                "$inc": {"balance": delta},
                "$push": {
                    "transactions": {
                        "type": kind,
                        "amount": abs(delta),
                        "at": datetime.utcnow(),
                    }
                },
            },
            projection={"balance": 1},
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise LookupError(f"Operation {kind} not applied for {self._user_id}")
        return doc["balance"]

    @staticmethod
    def _validate_amount(amount):
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError("amount must be a number")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("amount must be positive")
        return amount

    def close(self):
        """Close the underlying MongoDB connection."""
        self.client.close()

    def __repr__(self):
        return (
            f"BankAccount(user_id={self._user_id!r}, "
            f"owner_name={self._owner_name!r}, balance={self.get_balance():.2f})"
        )


if __name__ == "__main__":
    account = BankAccount(user_id="U1001", owner_name="Vineeth", initial_balance=500)
    print(account)
    print("deposit 250 ->", account.deposit(250))
    print("withdraw 100 ->", account.withdraw(100))
    print("balance ->", account.get_balance())

    other = BankAccount(user_id="U1002", owner_name="Rajan")
    other.deposit(50)
    print(other, "| first account unchanged:", account.get_balance())

    try:
        other.withdraw(1000)
    except InsufficientFundsError as exc:
        print("expected error:", exc)

    # Re-opening the same user sees the persisted balance.
    reopened = BankAccount(user_id="U1001")
    print("reopened balance ->", reopened.get_balance())
    print("last transaction ->", reopened.transactions[-1])

    for acct in (account, other, reopened):
        acct.close()
