"""Generate a Mockaroo-style MOCK_DATA.json file for the people search API."""

import json
import random

FIRST_NAMES = [
    "Aarav", "Abigail", "Aditya", "Alan", "Alice", "Amelia", "Ananya", "Andrew",
    "Anita", "Arjun", "Benjamin", "Bhavya", "Carlos", "Charlotte", "Chen",
    "Daniel", "Deepa", "Diego", "Elena", "Elijah", "Emma", "Ethan", "Farah",
    "Fatima", "Gabriel", "Grace", "Hannah", "Harsha", "Henry", "Ibrahim",
    "Isabella", "Ishaan", "Jacob", "James", "Jasmine", "Julia", "Karan",
    "Katherine", "Kavya", "Lars", "Laura", "Liam", "Lucas", "Maya", "Meera",
    "Michael", "Mohammed", "Nadia", "Nikhil", "Noah", "Olivia", "Omar",
    "Pooja", "Priya", "Rahul", "Ravi", "Rebecca", "Riya", "Samuel", "Sanjay",
    "Sara", "Sneha", "Sophia", "Tanvi", "Thomas", "Vikram", "Vineeth",
    "William", "Yusuf", "Zara",
]

LAST_NAMES = [
    "Acharya", "Ahmed", "Anderson", "Bakshi", "Bennett", "Bhatt", "Brown",
    "Carter", "Chandra", "Chen", "Clark", "Davis", "Desai", "Evans",
    "Fernandez", "Garcia", "Gupta", "Harris", "Iyer", "Jain", "Johnson",
    "Joshi", "Kapoor", "Khan", "Kumar", "Lewis", "Lopez", "Malhotra",
    "Martin", "Mehta", "Miller", "Mishra", "Nair", "Nguyen", "Patel",
    "Pillai", "Rajan", "Rajannagari", "Rao", "Reddy", "Roberts", "Sharma",
    "Shah", "Singh", "Smith", "Taylor", "Thomas", "Verma", "Walker", "Wilson",
]

GENDERS = ["Male", "Female", "Non-binary"]


def build_records(count: int) -> list[dict]:
    rng = random.Random(42)
    records = []
    for index in range(1, count + 1):
        first_name = rng.choice(FIRST_NAMES)
        last_name = rng.choice(LAST_NAMES)
        records.append(
            {
                "id": index,
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{first_name.lower()}.{last_name.lower()}{index}@example.com",
                "gender": rng.choice(GENDERS),
                "ip_address": ".".join(str(rng.randint(1, 254)) for _ in range(4)),
            }
        )
    return records


def main() -> None:
    records = build_records(1000)
    with open("MOCK_DATA.json", "w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2)
    print(f"Wrote {len(records)} records to MOCK_DATA.json")


if __name__ == "__main__":
    main()
