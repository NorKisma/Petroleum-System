from app import create_app, db
from app.models import FuelSale, FuelType
app = create_app()
with app.app_context():
    fuel_types = FuelType.query.all()
    print("Fuel Types:")
    for ft in fuel_types:
        print(f"- {ft.name}: sell={ft.sell_price}, buy={ft.buy_price}")
    
    sales = FuelSale.query.filter(FuelSale.sale_date < '2026-08-15').all()
    print(f"\nTotal sales before 15th: {len(sales)}")
    if sales:
        print("Sample sales before 15th:")
        for s in sales[:5]:
            print(f"- Date: {s.sale_date}, Liters: {s.liters_sold}, Unit Price: {s.unit_price}, Total: {s.total_amount}, Fuel: {s.fuel_type.name}")
