from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import (
    Tenant, Branch, Vendor, Customer,
    FuelType, FuelTank, FuelPump, FuelSale, FuelDelivery,
    FuelDipReading, FuelPriceHistory, FuelStockLedger,
    FuelPumpDailyLog, FuelDayClose, FleetProfile, FuelPumpShiftLog,
    FuelShift, User, Expense
)
from app.services.petroleum_service import PetroleumService
from app.utils.audit import log_audit
from app.utils.decorators import roles_required
from app.utils.module_access import module_required
from app.utils.datetime_utils import tenant_today, local_day_utc_bounds, tenant_now

petroleum = Blueprint('petroleum', __name__)

petroleum_required = module_required('petroleum')


@petroleum.route('/petroleum')
@login_required
@petroleum_required
def dashboard():
    tenant_id = current_user.tenant_id
    tanks = FuelTank.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    fuel_types = FuelType.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    pumps = FuelPump.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    tenant = db.session.get(Tenant, tenant_id)
    today = tenant_today(tenant)

    setup_complete = PetroleumService.is_setup_complete(tenant_id)
    summary = PetroleumService.get_day_summary(today)
    start_utc, end_utc = local_day_utc_bounds(today, tenant)
    recent_sales = FuelSale.query.filter_by(tenant_id=tenant_id)\
        .filter(FuelSale.sale_date >= start_utc, FuelSale.sale_date <= end_utc)\
        .order_by(FuelSale.sale_date.desc()).limit(10).all()
    recent_deliveries = FuelDelivery.query.filter_by(tenant_id=tenant_id)\
        .order_by(FuelDelivery.created_at.desc()).limit(5).all()
    low_tanks = [t for t in tanks if t.current_level <= t.min_alert_level]

    # Calculate Cash vs Credit inside summary
    cash_amount = sum(s.total_amount for s in summary['sales'] if s.payment_method != 'Credit')
    credit_amount = sum(s.total_amount for s in summary['sales'] if s.payment_method == 'Credit')
    summary['sales_cash'] = cash_amount
    summary['sales_credit'] = credit_amount

    # Get Fleet balance
    fleet_profiles = FleetProfile.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    fleet_debt_balance = sum(f.current_balance for f in fleet_profiles)

    return render_template('petroleum/dashboard.html',
                           tanks=tanks, fuel_types=fuel_types, pumps=pumps,
                           summary=summary, recent_sales=recent_sales,
                           recent_deliveries=recent_deliveries, low_tanks=low_tanks,
                           today=today, setup_complete=setup_complete, fleet_debt_balance=fleet_debt_balance)


# ─── Fuel Types ──────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/fuel-types')
@login_required
@petroleum_required
def fuel_types():
    types = FuelType.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelType.name).all()
    return render_template('petroleum/fuel_types.html', fuel_types=types)


@petroleum.route('/petroleum/fuel-types/add', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def add_fuel_type():
    data = request.get_json() or request.form
    try:
        ft = FuelType(
            name=data['name'],
            code=data.get('code', data['name'][:3].upper()),
            color_code=data.get('color_code', '#f59e0b'),
            buy_price=float(data.get('buy_price', 0)),
            sell_price=float(data.get('sell_price', 0)),
            tenant_id=current_user.tenant_id
        )
        db.session.add(ft)
        db.session.commit()
        log_audit('CREATE', 'PETROLEUM', f'Fuel type added: {ft.name}')
        return jsonify({'success': True, 'message': 'Nooca shidaalka waa la daray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/fuel-types/<int:id>/update', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def update_fuel_type(id):
    data = request.get_json() or request.form
    ft = FuelType.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        ft.name = data.get('name', ft.name)
        ft.code = data.get('code', ft.code)
        ft.color_code = data.get('color_code', ft.color_code)
        ft.is_active = data.get('is_active', ft.is_active) in (True, 'true', '1', 1)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Waa la cusboonaysiiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/fuel-types/<int:id>/price', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def change_fuel_price(id):
    data = request.get_json() or request.form
    try:
        PetroleumService.change_price(
            id,
            float(data['buy_price']),
            float(data['sell_price']),
            data.get('reason'),
            name=data.get('name'),
            code=data.get('code'),
            color_code=data.get('color_code')
        )
        db.session.commit()
        return jsonify({'success': True, 'message': 'Qiimaha waa la beddelay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@petroleum.route('/petroleum/fuel-types/<int:id>/delete', methods=['DELETE'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def delete_fuel_type(id):
    try:
        ft = FuelType.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
        # Check for dependencies
        if ft.tanks or ft.pumps:
            ft.is_active = False
            msg = 'Noocan waa la damiyay (Deactivated) maadaama ay ku xidhan yihiin Tanks ama Pumbad.'
        else:
            db.session.delete(ft)
            msg = 'Nooca shidaalka waa la tirtiray!'
        
        db.session.commit()
        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Tanks ───────────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/tanks')
@login_required
@petroleum_required
def tanks():
    all_tanks = FuelTank.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelTank.name).all()
    all_pumps = FuelPump.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelPump.pump_number).all()
    fuel_types = FuelType.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    branches = Branch.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('petroleum/tanks.html',
                           tanks=all_tanks, pumps=all_pumps, fuel_types=fuel_types, branches=branches)


@petroleum.route('/petroleum/tanks/add', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def add_tank():
    data = request.get_json() or request.form
    try:
        tank = FuelTank(
            name=data['name'],
            fuel_type_id=int(data['fuel_type_id']),
            branch_id=int(data['branch_id']) if data.get('branch_id') else None,
            capacity_liters=float(data.get('capacity_liters', 50000)),
            current_level=float(data.get('current_level', 0)),
            min_alert_level=float(data.get('min_alert_level', 5000)),
            tenant_id=current_user.tenant_id
        )
        db.session.add(tank)
        db.session.commit()
        log_audit('CREATE', 'PETROLEUM', f'Tank added: {tank.name}')
        return jsonify({'success': True, 'message': 'Tankiga waa la daray!', 'id': tank.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/tanks/<int:id>/update', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def update_tank(id):
    data = request.get_json() or request.form
    tank = FuelTank.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        tank.name = data.get('name', tank.name)
        tank.capacity_liters = float(data.get('capacity_liters', tank.capacity_liters))
        tank.min_alert_level = float(data.get('min_alert_level', tank.min_alert_level))
        tank.is_active = data.get('is_active', tank.is_active) in (True, 'true', '1', 1)
        if data.get('fuel_type_id'):
            tank.fuel_type_id = int(data['fuel_type_id'])
        if 'branch_id' in data:
            tank.branch_id = int(data['branch_id']) if data['branch_id'] else None
        db.session.commit()
        log_audit('UPDATE', 'PETROLEUM', f'Tank updated: {tank.name}')
        return jsonify({'success': True, 'message': 'Tankiga waa la cusboonaysiiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/tanks/<int:id>/delete', methods=['DELETE'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def delete_tank(id):
    tank = FuelTank.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    if len(tank.dip_readings) > 0:
        return jsonify({'success': False, 'message': 'This tank has associated readings and cannot be deleted.'})
    try:
        db.session.delete(tank)
        db.session.commit()
        log_audit('DELETE', 'PETROLEUM', f'Tank deleted: {tank.name}')
        return jsonify({'success': True, 'message': 'Tankiga waa la tirtiray.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Pumps ───────────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/pumps/add', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def add_pump():
    data = request.get_json() or request.form
    try:
        pump = FuelPump(
            pump_number=data['pump_number'],
            selling_price=float(data.get('selling_price', 0.0)),
            fuel_type_id=int(data['fuel_type_id']),
            tank_id=int(data['tank_id']),
            branch_id=int(data['branch_id']) if data.get('branch_id') else None,
            tenant_id=current_user.tenant_id
        )
        db.session.add(pump)
        db.session.commit()
        log_audit('CREATE', 'PETROLEUM', f'Pump added: {pump.pump_number}')
        return jsonify({'success': True, 'message': 'Pump-ka waa la daray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/pumps/<int:id>/delete', methods=['DELETE'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def delete_pump(id):
    pump = FuelPump.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        db.session.delete(pump)
        db.session.commit()
        log_audit('DELETE', 'PETROLEUM', f'Pump deleted: {pump.pump_number}')
        return jsonify({'success': True, 'message': 'Pump-ka waa la tirtiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Lama tirtiri karo. Waxaa laga yaabaa inuu la xiriiro xog kale.'})


@petroleum.route('/petroleum/pumps/<int:id>/update', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def update_pump(id):
    data = request.get_json() or request.form
    pump = FuelPump.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        pump.pump_number = data.get('pump_number', pump.pump_number)
        pump.selling_price = float(data.get('selling_price', pump.selling_price))
        if data.get('tank_id'):
            tank = FuelTank.query.filter_by(id=int(data['tank_id']), tenant_id=current_user.tenant_id).first()
            if tank:
                pump.tank_id = tank.id
                pump.fuel_type_id = tank.fuel_type_id
        if data.get('fuel_type_id'):
            pump.fuel_type_id = int(data['fuel_type_id'])
        if 'branch_id' in data:
            pump.branch_id = int(data['branch_id']) if data['branch_id'] else None
        pump.is_active = data.get('is_active', pump.is_active) in (True, 'true', '1', 1)
        db.session.commit()
        log_audit('UPDATE', 'PETROLEUM', f'Pump updated: {pump.pump_number}')
        return jsonify({'success': True, 'message': 'Pump-ka waa la cusboonaysiiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/pumps/<int:id>/meter', methods=['POST'])
@login_required
@petroleum_required
def log_pump_meter(id):
    data = request.get_json() or request.form
    pump = FuelPump.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        log_date = datetime.strptime(data.get('log_date', date.today().isoformat()), '%Y-%m-%d').date()
        existing = FuelPumpDailyLog.query.filter_by(
            pump_id=pump.id, log_date=log_date, tenant_id=current_user.tenant_id
        ).first()

        if existing:
            if data.get('opening_meter') is not None:
                existing.opening_meter = float(data['opening_meter'])
            if data.get('closing_meter') is not None:
                existing.closing_meter = float(data['closing_meter'])
        else:
            existing = FuelPumpDailyLog(
                pump_id=pump.id,
                log_date=log_date,
                opening_meter=float(data['opening_meter']) if data.get('opening_meter') else None,
                closing_meter=float(data['closing_meter']) if data.get('closing_meter') else None,
                user_id=current_user.id,
                tenant_id=current_user.tenant_id
            )
            db.session.add(existing)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Meter reading saved!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/pumps/<int:id>/shift-meter', methods=['POST'])
@login_required
@petroleum_required
def log_pump_shift_meter(id):
    data = request.get_json() or request.form
    try:
        log_date = datetime.strptime(data.get('log_date', date.today().isoformat()), '%Y-%m-%d').date()
        shift_number = int(data.get('shift_number', 1))
        PetroleumService.log_pump_shift_meter(
            id, log_date, shift_number,
            data.get('opening_meter'), data.get('closing_meter')
        )
        db.session.commit()
        return jsonify({'success': True, 'message': 'Akhriska shift-ka waa la kaydiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/shift-meters')
@login_required
@petroleum_required
def shift_meters():
    tenant = db.session.get(Tenant, current_user.tenant_id)
    target = request.args.get('date', tenant_today(tenant).isoformat())
    shift = int(request.args.get('shift', PetroleumService.detect_shift_number(tenant_now(tenant))))
    try:
        target_date = datetime.strptime(target, '%Y-%m-%d').date()
    except ValueError:
        target_date = tenant_today(tenant)

    pumps = FuelPump.query.filter_by(tenant_id=current_user.tenant_id, is_active=True)\
        .order_by(FuelPump.pump_number).all()
    logs = {}
    for pump in pumps:
        log = FuelPumpShiftLog.query.filter_by(
            pump_id=pump.id, log_date=target_date, shift_number=shift,
            tenant_id=current_user.tenant_id
        ).first()
        opening = log.opening_meter if log else None
        if opening is None and shift == 2:
            prev = FuelPumpShiftLog.query.filter_by(
                pump_id=pump.id, log_date=target_date, shift_number=1,
                tenant_id=current_user.tenant_id
            ).first()
            if prev and prev.closing_meter is not None:
                opening = prev.closing_meter
        logs[pump.id] = {
            'opening': opening,
            'closing': log.closing_meter if log else None,
        }

    shift_config_all = PetroleumService.get_shift_config(tenant)
    if shift not in shift_config_all:
        shift = 1
    shift_cfg = shift_config_all[shift]

    # Compute shift totals from meter logs
    total_liters = 0.0
    total_amount = 0.0
    total_profit = 0.0
    meter_total = 0.0
    for pump in pumps:
        log = logs.get(pump.id, {'opening': None, 'closing': None})
        if log['opening'] is not None and log['closing'] is not None and log['closing'] >= log['opening']:
            liters = log['closing'] - log['opening']
            price = pump.selling_price if pump.selling_price > 0 else pump.fuel_type.sell_price
            cost = pump.fuel_type.buy_price
            total_liters += liters
            total_amount += liters * price
            total_profit += liters * (price - cost)
            meter_total += liters

    from types import SimpleNamespace
    shift_totals = SimpleNamespace(
        total_liters=total_liters,
        total_amount=total_amount,
        total_profit=total_profit,
        meter_total=meter_total
    )

    # Shift Metadata
    shift_record = FuelShift.query.filter_by(
        log_date=target_date, shift_number=shift, tenant_id=current_user.tenant_id
    ).first()
    
    # Staff for dropdown
    staff = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    
    # Expenses for this shift
    shift_expenses = Expense.query.filter_by(fuel_shift_id=shift_record.id).all() if shift_record else []

    return render_template('petroleum/shift_meters.html',
                           pumps=pumps, logs=logs, target_date=target_date,
                           shift_number=shift, shift_cfg=shift_cfg, tenant=tenant,
                           shift_totals=shift_totals, shift_record=shift_record,
                           staff=staff, shift_expenses=shift_expenses)


@petroleum.route('/petroleum/shift-meta/save', methods=['POST'])
@login_required
@petroleum_required
def save_shift_meta():
    data = request.get_json()
    try:
        log_date = datetime.strptime(data['log_date'], '%Y-%m-%d').date()
        shift_num = int(data['shift_number'])
        tenant_id = current_user.tenant_id
        
        shift = FuelShift.query.filter_by(log_date=log_date, shift_number=shift_num, tenant_id=tenant_id).first()
        if not shift:
            shift = FuelShift(log_date=log_date, shift_number=shift_num, tenant_id=tenant_id)
            db.session.add(shift)
            
        # Security: Verify attendant belongs to tenant
        attendant_id = int(data.get('attendant_id')) if data.get('attendant_id') else None
        if attendant_id:
            valid_user = User.query.filter_by(id=attendant_id, tenant_id=tenant_id).first()
            if not valid_user:
                 return jsonify({'success': False, 'message': 'Shaqaalaha la doortay kama tirsana ganacsigan!'})
        
        shift.attendant_id = attendant_id
        shift.notes = data.get('notes')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Macluumaadka shift-ka waa la kaydiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/shift/bulk-save', methods=['POST'])
@login_required
@petroleum_required
def bulk_save_shift_data():
    data = request.get_json()
    try:
        log_date_str = data.get('log_date')
        if not log_date_str:
             return jsonify({'success': False, 'message': 'Taariikhda waa loo baahanyahy!'})
             
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
        shift_number = int(data.get('shift_number', 1))
        tenant_id = current_user.tenant_id
        
        # 1. Update Shift Metadata (Operator)
        shift_rec = FuelShift.query.filter_by(
            tenant_id=tenant_id,
            log_date=log_date,
            shift_number=shift_number
        ).first()
        
        if not shift_rec:
            shift_rec = FuelShift(
                tenant_id=tenant_id,
                log_date=log_date,
                shift_number=shift_number
            )
            db.session.add(shift_rec)
            
        # Security Check
        attendant_id = int(data.get('attendant_id')) if data.get('attendant_id') else None
        if attendant_id:
            valid_user = User.query.filter_by(id=attendant_id, tenant_id=tenant_id).first()
            if not valid_user:
                 return jsonify({'success': False, 'message': 'Shaqaalaha la doortay kama tirsana ganacsigan!'})

        shift_rec.attendant_id = attendant_id
        
        # 2. Update Pump Meter Readings
        meters = data.get('meters', [])
        for m in meters:
            pump_id = m.get('pump_id')
            opening = m.get('opening')
            closing = m.get('closing')
            if pump_id:
                PetroleumService.log_pump_shift_meter(
                    pump_id, log_date, shift_number, opening, closing
                )
                
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dhammaan xogta shift-ka waa la kaydiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Sales ───────────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/sales')
@login_required
@petroleum_required
def sales():
    all_sales = FuelSale.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelSale.sale_date.desc()).limit(200).all()
    pumps = FuelPump.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    tanks = FuelTank.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    fuel_types = FuelType.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    fleet = FleetProfile.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    staff = User.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    tenant = db.session.get(Tenant, current_user.tenant_id)
    return render_template('petroleum/sales.html',
                           sales=all_sales, pumps=pumps, tanks=tanks,
                           fuel_types=fuel_types, fleet=fleet, customers=customers,
                           staff=staff, tenant=tenant)


@petroleum.route('/petroleum/sales/add', methods=['POST'])
@login_required
@petroleum_required
def add_sale():
    data = request.get_json() or request.form
    try:
        PetroleumService.record_sale(data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Iibka shidaalka waa lagu guulaystay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/sales/<int:id>/update', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def update_sale(id):
    data = request.get_json() or request.form
    try:
        sale = PetroleumService.update_sale(id, data)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Iibka waa la cusboonaysiiyay!',
            'sale': {
                'id': sale.id,
                'liters_sold': sale.liters_sold,
                'unit_price': sale.unit_price,
                'total_amount': sale.total_amount,
                'vehicle_plate': sale.vehicle_plate,
                'driver_name': sale.driver_name,
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/sales/<int:id>/delete', methods=['DELETE'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def delete_sale(id):
    try:
        PetroleumService.delete_sale(id)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Iibka waa la tirtiray, stock-na waa la celiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Deliveries ──────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/deliveries')
@login_required
@petroleum_required
def deliveries():
    all_deliveries = FuelDelivery.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelDelivery.delivery_date.desc()).limit(200).all()
    tanks = FuelTank.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    fuel_types = FuelType.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    vendors = Vendor.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('petroleum/deliveries.html',
                           deliveries=all_deliveries, tanks=tanks,
                           fuel_types=fuel_types, vendors=vendors)


@petroleum.route('/petroleum/deliveries/add', methods=['POST'])
@login_required
@petroleum_required
def add_delivery():
    data = request.get_json() or request.form
    try:
        PetroleumService.record_delivery(data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Soo-dejinta waa lagu guulaystay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/deliveries/<int:id>/update', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def update_delivery(id):
    data = request.get_json() or request.form
    try:
        delivery = PetroleumService.update_delivery(id, data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Soo-dejinta waa la cusboonaysiiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/deliveries/<int:id>/delete', methods=['DELETE'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def delete_delivery(id):
    try:
        PetroleumService.delete_delivery(id)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Soo-dejinta waa la tirtiray, stock-na waa la celiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Morning Automation ───────────────────────────────────────────────────────

@petroleum.route('/petroleum/automation/morning-run', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def run_morning_automation_now():
    try:
        result = PetroleumService.run_morning_automation(current_user.tenant_id, force=True)
        db.session.commit()
        if result.get('skipped'):
            return jsonify({'success': True, 'message': f'Wax la qaban waayay: {result.get("reason", "unknown")}', 'result': result})
        return jsonify({
            'success': True,
            'message': f'Automation waa dhacay! Qiyaas: {result.get("opening_dips", 0)}, Xirid: {"Haa" if result.get("day_closed") else "Maya"}',
            'result': result
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Dip Readings ────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/dip-readings')
@login_required
@petroleum_required
def dip_readings():
    readings = FuelDipReading.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelDipReading.reading_date.desc()).limit(200).all()
    tanks = FuelTank.query.filter_by(tenant_id=current_user.tenant_id, is_active=True).all()
    tenant = db.session.get(Tenant, current_user.tenant_id)
    today_summary = PetroleumService.get_day_summary(tenant_today(tenant))
    return render_template('petroleum/dip_readings.html',
                           readings=readings, tanks=tanks,
                           tenant=tenant, today_summary=today_summary)


@petroleum.route('/petroleum/dip-readings/add', methods=['POST'])
@login_required
@petroleum_required
def add_dip_reading():
    data = request.get_json() or request.form
    data['apply_variance'] = data.get('apply_variance') in (True, 'true', '1', 1)
    try:
        PetroleumService.record_dip(data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dip reading waa la kaydiyay!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Fleet Customers ─────────────────────────────────────────────────────────

@petroleum.route('/petroleum/fleet')
@login_required
@petroleum_required
def fleet_customers():
    fleet = FleetProfile.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FleetProfile.created_at.desc()).all()
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('petroleum/fleet.html', fleet=fleet, customers=customers)


@petroleum.route('/petroleum/fleet/add', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def add_fleet_customer():
    data = request.get_json() or request.form
    try:
        customer_name = data.get('customer_name')
        phone = data.get('phone')
        
        if not customer_name:
            return jsonify({'success': False, 'message': 'Fadlan geli magaca macmiilka!'})
            
        # Find or create customer
        customer = Customer.query.filter_by(
            name=customer_name, 
            tenant_id=current_user.tenant_id
        ).first()
        
        if not customer:
            customer = Customer(
                name=customer_name,
                phone=phone,
                tenant_id=current_user.tenant_id
            )
            db.session.add(customer)
            db.session.flush()
            
        existing = FleetProfile.query.filter_by(
            customer_id=customer.id, 
            tenant_id=current_user.tenant_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Macmiilkan horey ayuu u ahaa fleet customer'})

        profile = FleetProfile(
            customer_id=customer.id,
            fleet_code=data.get('fleet_code', ''),
            credit_limit=float(data.get('credit_limit', 0)),
            payment_terms_days=int(data.get('payment_terms_days', 30)),
            tenant_id=current_user.tenant_id
        )
        db.session.add(profile)
        db.session.commit()
        log_audit('CREATE', 'PETROLEUM', f'Fleet customer added: {customer.name}')
        return jsonify({'success': True, 'message': 'Macmiilka Fleet-ka waa la daray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/fleet/<int:id>/payment', methods=['POST'])
@login_required
@petroleum_required
def fleet_payment(id):
    data = request.get_json() or request.form
    profile = FleetProfile.query.filter_by(id=id, tenant_id=current_user.tenant_id).first_or_404()
    try:
        amount = float(data.get('amount', 0))
        discount = float(data.get('discount', 0))
        total_deduction = amount + discount
        if total_deduction <= 0:
            raise ValueError('Amount or discount must be positive')
        if total_deduction > profile.current_balance:
            raise ValueError('Total payment and discount exceeds outstanding balance')
        PetroleumService.record_fleet_payment(
            profile, amount, data.get('payment_method', 'Cash'), discount
        )
        db.session.commit()
        return jsonify({'success': True, 'message': 'Lacag bixinta waa la kaydiyay!',
                        'new_balance': profile.current_balance})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Price History ───────────────────────────────────────────────────────────

@petroleum.route('/petroleum/prices')
@login_required
@petroleum_required
def price_history():
    history = FuelPriceHistory.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelPriceHistory.effective_date.desc()).limit(100).all()
    fuel_types = FuelType.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('petroleum/price_history.html',
                           history=history, fuel_types=fuel_types)


# ─── Stock Ledger & History Hub ──────────────────────────────────────────────

@petroleum.route('/petroleum/ledger')
@login_required
@petroleum_required
def stock_ledger():
    entries = FuelStockLedger.query.filter_by(tenant_id=current_user.tenant_id)\
        .order_by(FuelStockLedger.created_at.desc()).limit(300).all()
    tanks = FuelTank.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('petroleum/ledger.html', entries=entries, tanks=tanks)


@petroleum.route('/petroleum/history')
@login_required
@petroleum_required
def history_hub():
    tenant_id = current_user.tenant_id
    sales = FuelSale.query.filter_by(tenant_id=tenant_id)\
        .order_by(FuelSale.created_at.desc()).limit(50).all()
    deliveries = FuelDelivery.query.filter_by(tenant_id=tenant_id)\
        .order_by(FuelDelivery.created_at.desc()).limit(50).all()
    dips = FuelDipReading.query.filter_by(tenant_id=tenant_id)\
        .order_by(FuelDipReading.created_at.desc()).limit(50).all()
    prices = FuelPriceHistory.query.filter_by(tenant_id=tenant_id)\
        .order_by(FuelPriceHistory.created_at.desc()).limit(30).all()
    day_closes = FuelDayClose.query.filter_by(tenant_id=tenant_id)\
        .order_by(FuelDayClose.close_date.desc()).limit(30).all()
    return render_template('petroleum/history.html',
                           sales=sales, deliveries=deliveries, dips=dips,
                           prices=prices, day_closes=day_closes)


# ─── Profit Reports ─────────────────────────────────────────────────────────

@petroleum.route('/petroleum/reports/profit')
@login_required
@petroleum_required
def profit_reports():
    from datetime import timedelta
    tenant = db.session.get(Tenant, current_user.tenant_id)
    tenant_id = current_user.tenant_id
    today = tenant_today(tenant)

    period = request.args.get('period', 'daily')
    target = request.args.get('date', today.isoformat())
    try:
        target_date = datetime.strptime(target, '%Y-%m-%d').date()
    except ValueError:
        target_date = today

    # Determine date range
    if period == 'weekly':
        start_date = target_date - timedelta(days=target_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'monthly':
        start_date = target_date.replace(day=1)
        import calendar
        last_day = calendar.monthrange(target_date.year, target_date.month)[1]
        end_date = target_date.replace(day=last_day)
    elif period == 'yearly':
        start_date = target_date.replace(month=1, day=1)
        end_date = target_date.replace(month=12, day=31)
    else:  # daily
        start_date = target_date
        end_date = target_date

    start_utc, _ = local_day_utc_bounds(start_date, tenant)
    _, end_utc = local_day_utc_bounds(end_date, tenant)

    # Fetch all sales in range
    sales = FuelSale.query.filter_by(tenant_id=tenant_id).filter(
        FuelSale.sale_date >= start_utc,
        FuelSale.sale_date <= end_utc
    ).order_by(FuelSale.sale_date.asc()).all()

    # Fetch deliveries (purchases)
    deliveries = FuelDelivery.query.filter_by(tenant_id=tenant_id).filter(
        FuelDelivery.delivery_date >= start_utc,
        FuelDelivery.delivery_date <= end_utc
    ).all()

    # Fetch expenses
    from app.models import Expense
    expenses = Expense.query.filter_by(tenant_id=tenant_id).filter(
        Expense.created_at >= start_utc,
        Expense.created_at <= end_utc
    ).all()

    # Aggregate per pump
    pump_map = {}
    for s in sales:
        pid = s.pump_id or 0
        if pid not in pump_map:
            pump_map[pid] = {'liters': 0.0, 'revenue': 0.0, 'cost': 0.0, 'profit': 0.0,
                              'label': s.pump.pump_number if s.pump else 'Direct', 'count': 0}
        cost_price = s.pump.fuel_type.buy_price if s.pump else s.fuel_type.buy_price
        pump_map[pid]['liters'] += s.liters_sold
        pump_map[pid]['revenue'] += s.total_amount
        pump_map[pid]['cost'] += s.liters_sold * cost_price
        pump_map[pid]['profit'] += s.total_amount - (s.liters_sold * cost_price)
        pump_map[pid]['count'] += 1

    # Aggregate per fuel type
    fuel_map = {}
    for s in sales:
        fid = s.fuel_type_id
        if fid not in fuel_map:
            fuel_map[fid] = {'liters': 0.0, 'revenue': 0.0, 'cost': 0.0,
                              'profit': 0.0, 'label': s.fuel_type.name}
        cost_price = s.fuel_type.buy_price
        fuel_map[fid]['liters'] += s.liters_sold
        fuel_map[fid]['revenue'] += s.total_amount
        fuel_map[fid]['cost'] += s.liters_sold * cost_price
        fuel_map[fid]['profit'] += s.total_amount - (s.liters_sold * cost_price)

    # Aggregated totals
    total_revenue = sum(s.total_amount for s in sales)
    total_cost_goods = sum(s.liters_sold * (s.pump.fuel_type.buy_price if s.pump else s.fuel_type.buy_price) for s in sales)
    total_purchase_cost = sum(d.total_cost for d in deliveries)
    total_expenses = sum(e.amount for e in expenses)
    gross_profit = total_revenue - total_cost_goods
    net_profit = total_revenue - total_purchase_cost - total_expenses
    total_liters = sum(s.liters_sold for s in sales)

    # Daily breakdown for chart
    from collections import defaultdict
    daily = defaultdict(lambda: {'revenue': 0.0, 'profit': 0.0, 'liters': 0.0})
    for s in sales:
        day_key = s.sale_date.strftime('%Y-%m-%d')
        cost_p = s.pump.fuel_type.buy_price if s.pump else s.fuel_type.buy_price
        daily[day_key]['revenue'] += s.total_amount
        daily[day_key]['profit'] += s.total_amount - (s.liters_sold * cost_p)
        daily[day_key]['liters'] += s.liters_sold

    tanks = FuelTank.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    fuel_types = FuelType.query.filter_by(tenant_id=tenant_id, is_active=True).all()

    return render_template('petroleum/profit_reports.html',
                           period=period, target_date=target_date,
                           start_date=start_date, end_date=end_date,
                           sales=sales, deliveries=deliveries, expenses=expenses,
                           pump_data=list(pump_map.values()),
                           fuel_data=list(fuel_map.values()),
                           daily_data=dict(daily),
                           total_revenue=total_revenue,
                           total_cost_goods=total_cost_goods,
                           total_purchase_cost=total_purchase_cost,
                           total_expenses=total_expenses,
                           gross_profit=gross_profit,
                           net_profit=net_profit,
                           total_liters=total_liters,
                           tanks=tanks, fuel_types=fuel_types, tenant=tenant)


# ─── Daily Closing Report ────────────────────────────────────────────────────

@petroleum.route('/petroleum/reports/daily-closing')
@login_required
@petroleum_required
def daily_closing_report():
    tenant = db.session.get(Tenant, current_user.tenant_id)
    target = request.args.get('date', tenant_today(tenant).isoformat())
    try:
        target_date = datetime.strptime(target, '%Y-%m-%d').date()
    except ValueError:
        target_date = tenant_today(tenant)

    report = PetroleumService.get_daily_closing_report(target_date)
    return render_template('petroleum/daily_closing_report.html',
                           report=report, target_date=target_date, tenant=tenant)


@petroleum.route('/petroleum/reports/daily-closing/print')
@login_required
@petroleum_required
def daily_closing_report_print():
    tenant = db.session.get(Tenant, current_user.tenant_id)
    target = request.args.get('date', tenant_today(tenant).isoformat())
    try:
        target_date = datetime.strptime(target, '%Y-%m-%d').date()
    except ValueError:
        target_date = tenant_today(tenant)

    report = PetroleumService.get_daily_closing_report(target_date)
    return render_template('petroleum/daily_closing_report_print.html',
                           report=report, target_date=target_date, tenant=tenant)


# ─── Day Close ───────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/day-close')
@login_required
@petroleum_required
def day_close():
    tenant = db.session.get(Tenant, current_user.tenant_id)
    target = request.args.get('date', tenant_today(tenant).isoformat())
    try:
        target_date = datetime.strptime(target, '%Y-%m-%d').date()
    except ValueError:
        target_date = tenant_today(tenant)

    summary = PetroleumService.get_day_summary(target_date)
    closed = FuelDayClose.query.filter_by(
        tenant_id=current_user.tenant_id, close_date=target_date
    ).first()
    return render_template('petroleum/day_close.html',
                           summary=summary, closed=closed, tenant=tenant,
                           target_date=target_date)


@petroleum.route('/petroleum/day-close/execute', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def execute_day_close():
    data = request.get_json() or request.form
    try:
        tenant = db.session.get(Tenant, current_user.tenant_id)
        target_date = datetime.strptime(
            data.get('date', tenant_today(tenant).isoformat()), '%Y-%m-%d'
        ).date()
        PetroleumService.close_day(target_date, data.get('branch_id'), data.get('notes'))
        db.session.commit()
        return jsonify({'success': True, 'message': f'Maalinta {target_date} waa la xiray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ─── Setup / Seed ──────────────────────────────────────────────────────────────

@petroleum.route('/petroleum/setup')
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def setup_wizard():
    tenant_id = current_user.tenant_id
    fuel_types = FuelType.query.filter_by(tenant_id=tenant_id).all()
    branches = Branch.query.filter_by(tenant_id=tenant_id).all()
    customers = Customer.query.filter_by(tenant_id=tenant_id).all()
    setup_done = PetroleumService.is_setup_complete(tenant_id)
    return render_template('petroleum/setup.html',
                           fuel_types=fuel_types, branches=branches,
                           customers=customers, setup_done=setup_done)


@petroleum.route('/petroleum/setup/run', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def run_setup():
    data = request.get_json() or {}
    try:
        result = PetroleumService.run_initial_setup(current_user.tenant_id, data)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Setup complete! {result["tanks"]} tanks, {result["pumps"]} pumps, {result["fleet"]} fleet accounts.',
            'result': result
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@petroleum.route('/petroleum/setup/seed', methods=['POST'])
@login_required
@petroleum_required
@roles_required('admin', 'manager', 'developer')
def seed_defaults():
    data = request.get_json() or {}
    custom_types = data.get('custom_types')
    try:
        from app.services.accounting_service import AccountingService
        if custom_types:
            types_list = [(t['name'], t['code'], t.get('color', '#3b82f6'), float(t.get('buy', 0)), float(t.get('sell', 0))) for t in custom_types]
        else:
            types_list = None
        PetroleumService.seed_default_fuel_types(current_user.tenant_id, custom_types=types_list)
        AccountingService.ensure_petroleum_accounts(current_user.tenant_id)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Noocyada shidaalka & xisaabaadka waa la daray!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
