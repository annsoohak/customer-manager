"""Populate customer.db with deterministic Korean practice data."""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from time import perf_counter

from faker import Faker
from sqlalchemy import func, insert, select

from database import SessionLocal, engine
from models import Base, Customer, Employee, Order, Product


RANDOM_SEED = 20261114
REFERENCE_DATETIME = datetime(2026, 11, 14, 23, 59, 59)

CUSTOMER_COUNT = 10_000
PRODUCT_COUNT = 500
EMPLOYEE_COUNT = 300
ORDER_COUNT = 100_000
ORDER_BATCH_SIZE = 5_000

CATEGORIES = ("전자제품", "생활용품", "식품", "의류", "가구")
PRODUCT_WORDS = (
    "프리미엄",
    "스마트",
    "클래식",
    "데일리",
    "컴팩트",
    "에코",
    "베이직",
    "프로",
    "라이트",
    "시그니처",
)
DEPARTMENTS = ("영업", "고객지원", "물류", "마케팅", "재무", "인사")
JOB_TITLES = ("사원", "대리", "과장", "차장", "부장")
PAYMENT_METHODS = ("카드", "계좌이체", "현금", "간편결제")


def random_datetime(
    rng: random.Random, start: datetime, end: datetime
) -> datetime:
    """Return a uniformly distributed datetime in the inclusive range."""

    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=rng.randint(0, seconds))


def build_even_order_datetimes(
    rng: random.Random, start: datetime, end: datetime
) -> list[datetime]:
    """Spread order datetimes evenly across the full two-year interval."""

    total_seconds = (end - start).total_seconds()
    interval_seconds = total_seconds / ORDER_COUNT
    datetimes = [
        start
        + timedelta(seconds=(index + rng.random()) * interval_seconds)
        for index in range(ORDER_COUNT)
    ]
    rng.shuffle(datetimes)
    return datetimes


def build_customers(fake: Faker, rng: random.Random) -> tuple[list[dict], list[str]]:
    """Build exactly 5% VIP, 70% regular, and 25% new customers."""

    grades = ["VIP"] * 500 + ["일반"] * 7_000 + ["신규"] * 2_500
    rng.shuffle(grades)

    customers: list[dict] = []
    addresses: list[str] = []
    registration_start = REFERENCE_DATETIME - timedelta(days=365 * 5)

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        address = fake.address().replace("\n", " ")
        addresses.append(address)
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": fake.name(),
                "email": fake.unique.email(),
                "phone": fake.phone_number(),
                "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=80),
                "gender": rng.choice(("남성", "여성")),
                "city": fake.city(),
                "address": address,
                "grade": grades[customer_id - 1],
                "registered_at": random_datetime(
                    rng, registration_start, REFERENCE_DATETIME
                ),
                "is_active": rng.random() < 0.97,
            }
        )

    return customers, addresses


def build_products(fake: Faker, rng: random.Random) -> tuple[list[dict], list[int]]:
    """Build 500 products spread evenly across five categories."""

    categories = [category for category in CATEGORIES for _ in range(100)]
    rng.shuffle(categories)

    products: list[dict] = []
    prices: list[int] = []
    registration_start = REFERENCE_DATETIME - timedelta(days=365 * 4)

    for product_id in range(1, PRODUCT_COUNT + 1):
        category = categories[product_id - 1]
        price = rng.randint(1, 2_000) * 1_000
        prices.append(price)
        products.append(
            {
                "product_id": product_id,
                "product_name": (
                    f"{category} {PRODUCT_WORDS[(product_id - 1) % len(PRODUCT_WORDS)]} "
                    f"{product_id:03d}"
                ),
                "category": category,
                "unit_price": price,
                "cost_price": int(price * rng.uniform(0.55, 0.85)),
                "stock_quantity": rng.randint(0, 2_000),
                "supplier_name": fake.company(),
                "registered_at": random_datetime(
                    rng, registration_start, REFERENCE_DATETIME
                ),
                "is_active": rng.random() < 0.95,
            }
        )

    return products, prices


def build_employees(fake: Faker, rng: random.Random) -> list[dict]:
    """Build employee master data."""

    employees: list[dict] = []
    hire_start = date(2005, 1, 1)
    hire_span = (REFERENCE_DATETIME.date() - hire_start).days

    for employee_id in range(1, EMPLOYEE_COUNT + 1):
        employees.append(
            {
                "employee_id": employee_id,
                "employee_name": fake.name(),
                "department": rng.choice(DEPARTMENTS),
                "job_title": rng.choice(JOB_TITLES),
                "email": fake.unique.company_email(),
                "phone": fake.phone_number(),
                "hire_date": hire_start + timedelta(days=rng.randint(0, hire_span)),
                "salary": rng.randrange(30_000_000, 121_000_000, 1_000_000),
                "is_active": rng.random() < 0.95,
            }
        )

    return employees


def build_order_statuses(rng: random.Random) -> list[str]:
    """Build the exact 90%/7%/3% requested order-status distribution."""

    statuses = ["완료"] * 90_000 + ["배송중"] * 7_000 + ["취소"] * 3_000
    rng.shuffle(statuses)
    return statuses


def seed_database() -> None:
    """Replace existing rows with deterministic practice data."""

    started_at = perf_counter()
    rng = random.Random(RANDOM_SEED)
    Faker.seed(RANDOM_SEED)
    fake = Faker("ko_KR")
    fake.seed_instance(RANDOM_SEED)
    fake.unique.clear()

    # Every run starts from a completely new schema and an empty database.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print(f"랜덤 시드: {RANDOM_SEED}")
    print(f"주문 기준일: {REFERENCE_DATETIME:%Y-%m-%d}")
    print("기존 테이블 DROP 및 재생성 완료")
    print("더미 데이터 생성 중...")

    customers, customer_addresses = build_customers(fake, rng)
    products, product_prices = build_products(fake, rng)
    employees = build_employees(fake, rng)
    statuses = build_order_statuses(rng)

    order_start = REFERENCE_DATETIME - timedelta(days=730)
    order_datetimes = build_even_order_datetimes(
        rng, order_start, REFERENCE_DATETIME
    )

    with SessionLocal() as session:
        # ORM 객체를 한 건씩 만들지 않고 executemany bulk insert를 사용한다.
        session.execute(insert(Customer), customers)
        session.execute(insert(Product), products)
        session.execute(insert(Employee), employees)
        print("마스터 데이터 bulk insert 완료")

        order_id = 1
        for batch_start in range(0, ORDER_COUNT, ORDER_BATCH_SIZE):
            batch: list[dict] = []
            batch_end = min(batch_start + ORDER_BATCH_SIZE, ORDER_COUNT)

            for status_index in range(batch_start, batch_end):
                customer_id = rng.randint(1, CUSTOMER_COUNT)
                product_id = rng.randint(1, PRODUCT_COUNT)
                employee_id = rng.randint(1, EMPLOYEE_COUNT)
                quantity = rng.randint(1, 5)
                order_date = order_datetimes[status_index]
                status = statuses[status_index]

                shipped_date = None
                if status == "완료":
                    shipped_date = min(
                        (order_date + timedelta(days=rng.randint(1, 7))).date(),
                        REFERENCE_DATETIME.date(),
                    )

                batch.append(
                    {
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "product_id": product_id,
                        "employee_id": employee_id,
                        "order_date": order_date,
                        "quantity": quantity,
                        "unit_price": product_prices[product_id - 1],
                        "discount_amount": 0,
                        "order_status": status,
                        "payment_method": rng.choice(PAYMENT_METHODS),
                        "shipping_address": customer_addresses[customer_id - 1],
                        "shipped_date": shipped_date,
                    }
                )
                order_id += 1

            session.execute(insert(Order), batch)
            print(f"주문 bulk insert: {batch_end:,}/{ORDER_COUNT:,}")

        session.commit()

        counts = {
            "customers": session.scalar(select(func.count()).select_from(Customer)),
            "products": session.scalar(select(func.count()).select_from(Product)),
            "employees": session.scalar(select(func.count()).select_from(Employee)),
            "orders": session.scalar(select(func.count()).select_from(Order)),
        }

        grade_counts = dict(
            session.execute(
                select(Customer.grade, func.count())
                .group_by(Customer.grade)
                .order_by(Customer.grade)
            ).all()
        )
        status_counts = dict(
            session.execute(
                select(Order.order_status, func.count())
                .group_by(Order.order_status)
                .order_by(Order.order_status)
            ).all()
        )

    print("\n테이블별 건수")
    for table_name, count in counts.items():
        print(f"- {table_name}: {count:,}")
    print(f"고객 등급 분포: {grade_counts}")
    print(f"주문 상태 분포: {status_counts}")
    print(f"완료 시간: {perf_counter() - started_at:.2f}초")


if __name__ == "__main__":
    seed_database()
