from app import create_app
from app.services.petroleum_service import PetroleumService
from datetime import date
app = create_app()

with app.app_context():
    target_date = date(2026, 8, 11)
    report = PetroleumService.get_daily_closing_report(target_date, tenant_id=1)
    shift = report['shifts'][0]  # shift 1
    for p in shift['pumps']:
        print(f"Pump {p['pump_number']}: opening={p['opening_meter']}, closing={p['closing_meter']}, price={p['unit_price']}, amount={p['total_amount']}")
