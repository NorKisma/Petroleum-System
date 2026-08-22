from app import create_app, db
from app.models import FuelPump, FuelSale, FuelPriceHistory
from datetime import date
from app.services.petroleum_service import PetroleumService
app = create_app()

with app.app_context():
    pumps = FuelPump.query.all()
    target_date = date(2026, 8, 11)
    for pump in pumps:
        price = PetroleumService.get_historical_pump_price(pump, target_date, pump.tenant_id)
        print(f"Pump {pump.pump_number} price on {target_date}: {price}")
