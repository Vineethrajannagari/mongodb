"""
Simple bank account with deposit, withdraw and balance operations.

Each BankAccount instance belongs to exactly one user: the owner is set at
construction time and cannot be changed afterwards.
"""


class InsufficientFundsError(Exception):
    """Raised when a withdrawal exceeds the available balance."""


class BankAccount:
    """A bank account owned by a single user."""

    def __init__(self, user_id, owner_name, initial_balance=0.0):
        """
        Args:
            user_id: Unique identifier of the user owning this account
            owner_name: Display name of the owner
            initial_balance: Opening balance, must not be negative

        Raises:
            ValueError: If user_id is empty or initial_balance is negative
        """
        if not user_id:
            raise ValueError("user_id is required")
        if initial_balance < 0:
            raise ValueError("initial_balance cannot be negative")

        self._user_id = user_id
        self._owner_name = owner_name
        self._balance = float(initial_balance)
        self._transactions = []

    @property
    def user_id(self):
        return self._user_id

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def transactions(self):
        return list(self._transactions)

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
        self._balance += amount
        self._transactions.append(("deposit", amount, self._balance))
        return self._balance

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
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount:.2f}: balance is {self._balance:.2f}"
            )
        self._balance -= amount
        self._transactions.append(("withdraw", amount, self._balance))
        return self._balance

    def get_balance(self):
        """Return the current balance."""
        return self._balance

    @staticmethod
    def _validate_amount(amount):
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError("amount must be a number")
        amount = float(amount)
        if amount <= 0:
            raise ValueError("amount must be positive")
        return amount

    def __repr__(self):
        return (
            f"BankAccount(user_id={self._user_id!r}, "
            f"owner_name={self._owner_name!r}, balance={self._balance:.2f})"
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
