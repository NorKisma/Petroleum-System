from app import create_app, db
from app.models import FuelPump, FuelSale, FuelPriceHistory
from datetime import date
app = create_app()

def get_historical_pump_price(pump, target_date, tenant_id):
    last_sale = FuelSale.query.filter_by(tenant_id=tenant_id, pump_id=pump.id).filter(
        db.func.date(FuelSale.sale_date) <= target_date
    ).order_by(FuelSale.sale_date.desc()).first()
    
    if last_sale:
        return last_sale.unit_price
        
    history_before = FuelPriceHistory.query.filter_by(tenant_id=tenant_id, fuel_type_id=pump.fuel_type_id).filter(
        db.func.date(FuelPriceHistory.created_at) <= target_date
    ).order_by(FuelPriceHistory.created_at.desc()).first()
    
    if history_before:
        return history_before.new_sell_price
        
    history_after = FuelPriceHistory.query.filter_by(tenant_id=tenant_id, fuel_type_id=pump.fuel_type_id).filter(
        db.func.date(FuelPriceHistory.created_at) > target_date
    ).order_by(FuelPriceHistory.created_at.asc()).first()
    
    if history_after:
        return history_after.old_sell_price

    return pump.selling_price if pump.selling_price > 0 else (pump.fuel_type.sell_price if pump.fuel_type else 0)

with app.app_context():
    pumps = FuelPump.query.all()
    target_date = date(2026, 8, 14)
    for pump in pumps:
        price = get_historical_pump_price(pump, target_date, pump.tenant_id)
        print(f"Pump {pump.pump_number} ({pump.fuel_type.name}) price on {target_date}: {price}")

