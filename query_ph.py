from app import create_app, db
from app.models import FuelPriceHistory, FuelType
app = create_app()
with app.app_context():
    history = FuelPriceHistory.query.order_by(FuelPriceHistory.created_at.desc()).all()
    for h in history:
        fuel = FuelType.query.get(h.fuel_type_id)
        print(f"Created: {h.created_at}, Fuel: {fuel.name}, Old Sell: {h.old_sell_price}, New Sell: {h.new_sell_price}")
