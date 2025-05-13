from confluent_kafka import Producer
import json
from faker import Faker
import random
from datetime import datetime
import time

KAFKA_TOPIC = "3_orders"

fake = Faker()
PRODUCTS = {
    "Laptop": (500, 2000),
    "Smartphone": (300, 1500),
    "Tablet": (200, 800),
    "Smartwatch": (100, 500),
    "Headphones": (50, 300),
    "Camera": (300, 2000),
    "Printer": (100, 500),
    "Speaker": (50, 400),
    "Monitor": (100, 600),
    "Keyboard": (20, 150)
}
STATUSES = ["Shipped", "Pending", "Completed"]
STATES = ["Illinois", "Indiana", "Iowa", "Kansas", "Michigan", "Minnesota", "Missouri", "Nebraska", "Ohio", "Wisconsin"]


producer = Producer({'bootstrap.servers': 'localhost:29098',
                     'client.id' :  'producer'})


def generate_order_data():
    product_type = random.choice(list(PRODUCTS.keys()))
    price_range = PRODUCTS[product_type]
    unit_price = round(random.uniform(price_range[0], price_range[1]), 2)  # สุ่มราคาต่อชิ้นในช่วงที่กำหนด
    quantity = random.randint(1, 5)
    total_price = round(unit_price * quantity, 2)  # คำนวณราคาทั้งหมดจาก UNIT_PRICE และ QUANTITY

    order_data = {
        "ORDERID": str(fake.uuid4()),
        "USERID": "User_" + str(random.randint(1, 9)),
        "ORDER_TIMESTAMP": datetime.now().isoformat(),
        "PRODUCT_TYPE": product_type,
        "UNIT_PRICE": unit_price,  # เพิ่มราคาต่อหน่วย
        "QUANTITY": quantity,
        "TOTAL_PRICE": total_price,
        "STATE": random.choice(STATES),
        "STATUS": random.choice(STATUSES)
    }

    return order_data

def produce_orders():
    while True:
        order_message = generate_order_data()
        key = order_message["USERID"]
        value = json.dumps(order_message)

        try:
            producer.produce(topic=KAFKA_TOPIC, key=key, value=value)
            print(f"Sent: {order_message}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

    producer.flush()

if __name__ == "__main__":
    try:
        produce_orders()
    except KeyboardInterrupt:
        print("Order data production stopped.")
    finally:
        producer.flush()

