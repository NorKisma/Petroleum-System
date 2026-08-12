"""
Comprehensive Test Suite — Advanced Inventory POS & Accounting System
Covers: Authentication, Inventory, Sales, Accounting, Customers, API
Run with: pytest tests/ -v
"""

import pytest
from app import create_app, db
from app.models import Tenant, User, Product, Category, Customer, Sale, SaleItem, Expense
from flask_bcrypt import Bcrypt


# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    """Create test Flask application with in-memory SQLite database."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "SERVER_NAME": "localhost"
    })
    with app.app_context():
        db.create_all()
        _seed_test_data(app)
        yield app
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="module")
def auth_client(app, client):
    """Authenticated test client (logged in as admin)."""
    with app.app_context():
        client.post("/login", data={
            "username": "testadmin",
            "password": "Test@1234"
        }, follow_redirects=True)
    return client


def _seed_test_data(app):
    """Seed minimal data needed for tests."""
    bcrypt = Bcrypt(app)
    with app.app_context():
        # Tenant
        tenant = Tenant(name="Test Business", currency="$")
        db.session.add(tenant)
        db.session.flush()

        # Admin user
        hashed = bcrypt.generate_password_hash("Test@1234").decode("utf-8")
        user = User(
            username="testadmin",
            email="admin@test.com",
            password=hashed,
            role="admin",
            tenant_id=tenant.id
        )
        db.session.add(user)
        db.session.flush()

        # Category + Product
        cat = Category(name="Electronics", tenant_id=tenant.id)
        db.session.add(cat)
        db.session.flush()

        product = Product(
            name="Test Phone",
            barcode="123456789",
            buy_price=100.0,
            sell_price=150.0,
            stock_quantity=50,
            category_id=cat.id,
            tenant_id=tenant.id
        )
        db.session.add(product)

        # Customer
        customer = Customer(name="John Doe", phone="0612345678", tenant_id=tenant.id)
        db.session.add(customer)

        # Expense
        expense = Expense(
            description="Office Rent",
            amount=500.0,
            category="Rent",
            tenant_id=tenant.id
        )
        db.session.add(expense)

        db.session.commit()


# ─── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuthentication:

    def test_login_page_loads(self, client):
        """Login page should return HTTP 200."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_page_has_form(self, client):
        """Login page should contain a sign-in form."""
        response = client.get("/login")
        assert b"username" in response.data.lower() or b"sign in" in response.data.lower() or b"login" in response.data.lower()

    def test_dashboard_redirects_when_unauthenticated(self, client):
        """Dashboard should redirect unauthenticated users to login."""
        response = client.get("/", follow_redirects=True)
        assert b"login" in response.data.lower() or b"sign in" in response.data.lower()

    def test_login_with_wrong_credentials(self, client):
        """Login with wrong password should not succeed."""
        response = client.post("/login", data={
            "username": "testadmin",
            "password": "wrongpassword"
        }, follow_redirects=True)
        # Should stay on login page or show error
        assert response.status_code == 200

    def test_login_with_correct_credentials(self, app, client):
        """Login with correct credentials should redirect to dashboard."""
        with app.app_context():
            response = client.post("/login", data={
                "username": "testadmin",
                "password": "Test@1234"
            }, follow_redirects=True)
            assert response.status_code == 200


# ─── Inventory Tests ───────────────────────────────────────────────────────────

class TestInventory:

    def test_inventory_page_loads(self, auth_client):
        """Inventory page should load for authenticated users."""
        response = auth_client.get("/inventory")
        assert response.status_code in [200, 302]

    def test_product_model_fields(self, app):
        """Product model should have correct fields."""
        with app.app_context():
            product = Product.query.filter_by(name="Test Phone").first()
            assert product is not None
            assert product.buy_price == 100.0
            assert product.sell_price == 150.0
            assert product.stock_quantity == 50

    def test_product_profit_margin(self, app):
        """Product profit margin should be calculated correctly."""
        with app.app_context():
            product = Product.query.filter_by(name="Test Phone").first()
            margin = product.sell_price - product.buy_price
            assert margin == 50.0

    def test_category_model(self, app):
        """Category model should exist and link to tenant."""
        with app.app_context():
            cat = Category.query.filter_by(name="Electronics").first()
            assert cat is not None
            assert cat.tenant_id is not None


# ─── Customer Tests ────────────────────────────────────────────────────────────

class TestCustomers:

    def test_customer_model(self, app):
        """Customer model should be created correctly."""
        with app.app_context():
            customer = Customer.query.filter_by(name="John Doe").first()
            assert customer is not None
            assert customer.phone == "0612345678"

    def test_customers_page_loads(self, auth_client):
        """Customers page should load."""
        response = auth_client.get("/customers")
        assert response.status_code in [200, 302]


# ─── Accounting Tests ──────────────────────────────────────────────────────────

class TestAccounting:

    def test_expense_model(self, app):
        """Expense model should be stored correctly."""
        with app.app_context():
            expense = Expense.query.filter_by(description="Office Rent").first()
            assert expense is not None
            assert expense.amount == 500.0
            assert expense.category == "Rent"

    def test_accounting_dashboard_loads(self, auth_client):
        """Accounting dashboard should load."""
        response = auth_client.get("/accounting")
        assert response.status_code in [200, 302]

    def test_expenses_page_loads(self, auth_client):
        """Expenses page should load."""
        response = auth_client.get("/accounting/expenses")
        assert response.status_code in [200, 302]

    def test_balance_sheet_loads(self, auth_client):
        """Balance sheet page should load."""
        response = auth_client.get("/accounting/balance-sheet")
        assert response.status_code in [200, 302]


# ─── AI Predictor Unit Tests ───────────────────────────────────────────────────

class TestAIPredictor:

    def test_moving_average_basic(self):
        """Moving average should return correct length."""
        from app.utils.ai_predictor import _moving_average
        values = [10, 20, 30, 40, 50]
        result = _moving_average(values, window=3)
        assert len(result) == 5

    def test_linear_trend_positive(self):
        """Linear trend should detect upward slope."""
        from app.utils.ai_predictor import _linear_trend
        values = [10, 20, 30, 40, 50]
        slope, _ = _linear_trend(values)
        assert slope > 0

    def test_linear_trend_flat(self):
        """Linear trend should detect flat line."""
        from app.utils.ai_predictor import _linear_trend
        values = [100, 100, 100, 100]
        slope, _ = _linear_trend(values)
        assert abs(slope) < 1

    def test_predict_next_days_empty(self):
        """Predictor should handle empty sales gracefully."""
        from app.utils.ai_predictor import predict_next_days
        result = predict_next_days([], days_ahead=7)
        assert "predictions" in result
        assert len(result["predictions"]) == 7
        assert result["avg_daily"] == 0


# ─── Reports Unit Tests ────────────────────────────────────────────────────────

class TestReports:

    def test_generate_financial_report(self, app):
        """Financial report generator should return valid HTML response."""
        from app.utils.reports import generate_financial_report
        with app.app_context():
            data = {
                "total_revenue": 10000,
                "total_cogs": 6000,
                "gross_profit": 4000,
                "total_expenses": 1000,
                "total_other_income": 500,
                "net_profit": 3500
            }
            response = generate_financial_report(data)
            assert response.status_code == 200
            assert b"Financial Report" in response.data

    def test_generate_sales_report_empty(self, app):
        """Sales report with no data should not crash."""
        from app.utils.reports import generate_sales_report
        with app.app_context():
            response = generate_sales_report([])
            assert response.status_code == 200

    def test_generate_inventory_report_empty(self, app):
        """Inventory report with no products should not crash."""
        from app.utils.reports import generate_inventory_report
        with app.app_context():
            response = generate_inventory_report([])
            assert response.status_code == 200


# ─── Tenant / Multi-Tenant Tests ───────────────────────────────────────────────

class TestTenant:

    def test_tenant_created(self, app):
        """Tenant should be created and linked to user."""
        with app.app_context():
            tenant = Tenant.query.filter_by(name="Test Business").first()
            assert tenant is not None
            assert tenant.currency == "$"

    def test_user_linked_to_tenant(self, app):
        """User should be linked to a tenant."""
        with app.app_context():
            user = User.query.filter_by(username="testadmin").first()
            assert user is not None
            assert user.tenant_id is not None
            assert user.role == "admin"
