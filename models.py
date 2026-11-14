"""Customer management database models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class shared by all ORM models."""


class Customer(Base):
    """Customer master data."""

    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("email", name="uq_customers_email"),
        CheckConstraint("is_active IN (0, 1)", name="ck_customers_is_active"),
    )

    customer_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="고객 식별자"
    )
    customer_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="고객명"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="고객 이메일"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="고객 전화번호"
    )
    birth_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="생년월일"
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="성별 또는 구분값"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="거주 도시"
    )
    address: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="상세 주소"
    )
    grade: Mapped[str] = mapped_column(
        String(10), nullable=False, default="일반", comment="고객등급"
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="고객 가입 일시"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="고객 활성 여부"
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="customer", lazy="selectin"
    )


class Product(Base):
    """Product master data."""

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="ck_products_unit_price"),
        CheckConstraint("cost_price IS NULL OR cost_price >= 0", name="ck_products_cost_price"),
        CheckConstraint("stock_quantity >= 0", name="ck_products_stock_quantity"),
        CheckConstraint("is_active IN (0, 1)", name="ck_products_is_active"),
    )

    product_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="상품 식별자"
    )
    product_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="상품명"
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="상품 분류"
    )
    unit_price: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="현재 판매가격(원)"
    )
    cost_price: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="상품 원가(원)"
    )
    stock_quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="현재 재고 수량"
    )
    supplier_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="공급업체명"
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, comment="상품 등록 일시"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="상품 판매 여부"
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="product", lazy="selectin"
    )


class Employee(Base):
    """Employee master data."""

    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("email", name="uq_employees_email"),
        CheckConstraint("salary IS NULL OR salary >= 0", name="ck_employees_salary"),
        CheckConstraint("is_active IN (0, 1)", name="ck_employees_is_active"),
    )

    employee_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="직원 식별자"
    )
    employee_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="직원명"
    )
    department: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="소속 부서"
    )
    job_title: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="직급 또는 직책"
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="회사 이메일"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="직원 연락처"
    )
    hire_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="입사일"
    )
    salary: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="급여(원)"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="직원 재직 여부"
    )

    orders: Mapped[list[Order]] = relationship(
        back_populates="employee", lazy="selectin"
    )


class Order(Base):
    """One product line ordered by a customer."""

    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_orders_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_orders_unit_price"),
        CheckConstraint("discount_amount >= 0", name="ck_orders_discount_amount"),
        CheckConstraint(
            "discount_amount <= quantity * unit_price",
            name="ck_orders_discount_not_over_total",
        ),
    )

    order_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="주문 식별자"
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="주문 고객 식별자",
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="주문 상품 식별자",
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.employee_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="담당 직원 식별자",
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, comment="주문 일시(최근 2년 범위)"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="주문 수량"
    )
    unit_price: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="주문 당시 상품 단가(원)"
    )
    discount_amount: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="할인 금액(원)"
    )
    order_amount: Mapped[int] = mapped_column(
        Integer,
        Computed("quantity * unit_price - discount_amount", persisted=True),
        comment="최종 주문 금액(자동 계산)",
    )
    order_status: Mapped[str] = mapped_column(
        String(30), nullable=False, comment="주문 상태"
    )
    payment_method: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="결제 수단"
    )
    shipping_address: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="주문 당시 배송 주소"
    )
    shipped_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="배송일"
    )

    customer: Mapped[Customer] = relationship(back_populates="orders")
    product: Mapped[Product] = relationship(back_populates="orders")
    employee: Mapped[Employee] = relationship(back_populates="orders")

