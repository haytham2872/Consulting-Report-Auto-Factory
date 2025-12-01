import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_orders(num_orders: int = 200):
    random.seed(42)
    start_date = datetime.today() - timedelta(days=540)
    categories = ["Electronics", "Home", "Fashion", "Sports", "Beauty"]
    countries = ["Germany", "France", "United Kingdom", "United States", "Canada", "Spain"]
    records = []
    for i in range(num_orders):
        order_date = start_date + timedelta(days=random.randint(0, 540))
        customer_id = random.randint(1, 120)
        category = random.choice(categories)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(15, 350), 2)
        discount = round(random.uniform(0, 0.15), 2)
        total_amount = round(quantity * unit_price * (1 - discount), 2)
        records.append(
            [
                f"ORD-{1000+i}",
                order_date.date().isoformat(),
                customer_id,
                random.choice(countries),
                category,
                quantity,
                unit_price,
                discount,
                total_amount,
            ]
        )
    return records


def generate_customers(num_customers: int = 120):
    random.seed(99)
    segments = ["Consumer", "SMB", "Enterprise"]
    start_date = datetime.today() - timedelta(days=720)
    records = []
    for cid in range(1, num_customers + 1):
        signup_date = start_date + timedelta(days=random.randint(0, 700))
        lifetime_value = round(random.uniform(200, 7000), 2)
        is_churned = random.random() < 0.2
        records.append(
            [
                cid,
                signup_date.date().isoformat(),
                random.choice(segments),
                lifetime_value,
                is_churned,
            ]
        )
    return records


def main():
    output_dir = Path("data/input")
    output_dir.mkdir(parents=True, exist_ok=True)

    orders = generate_orders()
    customers = generate_customers()

    with open(output_dir / "orders.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "order_id",
                "order_date",
                "customer_id",
                "country",
                "product_category",
                "quantity",
                "unit_price",
                "discount",
                "total_amount",
            ]
        )
        writer.writerows(orders)

    with open(output_dir / "customers.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "signup_date", "segment", "lifetime_value", "is_churned"])
        writer.writerows(customers)

    print(f"Wrote {len(orders)} orders and {len(customers)} customers to {output_dir}")


if __name__ == "__main__":
    main()
