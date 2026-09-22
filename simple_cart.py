class Item:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"{self.name}: ${self.price} x {self.quantity}"


class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        for item in self.items:
            if item.name == item_name:
                self.items.remove(item)
                return

        print("Item not found")

    def get_total(self):
        total = 0

        for item in self.items:
            total += item.price * item.quantity

        return total


item1 = Item("Laptop", 50000, 1)
item2 = Item("Mouse", 1000, 2)


cart = Cart()


cart.add_item(item1)
cart.add_item(item2)


print("Total: $", cart.get_total())
