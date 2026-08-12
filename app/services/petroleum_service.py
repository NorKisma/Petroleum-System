from datetime import datetime, date, timedelta, time
from app import db
from app.models import (
    FuelType, FuelTank, FuelPump, FuelSale, FuelDelivery,
    FuelDipReading, FuelPriceHistory, FuelStockLedger,
    FuelPumpDailyLog, FuelPumpShiftLog, FuelDayClose, FleetProfile, Tenant, User
)
from app.utils.audit import log_audit
from app.utils.datetime_utils import (
    tenant_today, tenant_now, local_day_utc_bounds, end_of_local_day_utc,
    get_tenant_timezone, local_datetime_to_utc_naive, utc_naive_to_local,
)


class PetroleumService:

    @staticmethod
    def _tenant_id():
        from flask_login import current_user
        return current_user.tenant_id

    @staticmethod
    def _user_id():
        from flask_login import current_user
        return current_user.id

    @staticmethod
    def update_tank_level(tank, liters_delta):
        tank.current_level = round((tank.current_level or 0) + liters_delta, 2)
        if tank.current_level < 0:
            raise ValueError(f'Tank {tank.name}: stock cannot go negative ({tank.current_level} L)')

    @staticmethod
    def add_ledger_entry(tank, fuel_type_id, txn_type, ref_id, ref_no,
                         liters_in, liters_out, unit_cost=None, notes=None):
        entry = FuelStockLedger(
            fuel_type_id=fuel_type_id,
            tank_id=tank.id,
            transaction_type=txn_type,
            reference_id=ref_id,
            reference_no=ref_no,
            liters_in=liters_in,
            liters_out=liters_out,
            balance_after=tank.current_level,
            unit_cost=unit_cost,
            notes=notes,
            user_id=PetroleumService._user_id(),
            tenant_id=PetroleumService._tenant_id()
        )
        db.session.add(entry)
        return entry

    @staticmethod
    def record_sale(data):
        pump_id = data.get('pump_id')
        if not pump_id:
            raise ValueError('All fuel sales must be recorded through a pump')
            
        pump = FuelPump.query.filter_by(
            id=pump_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        
        tank = pump.tank
        fuel_type = pump.fuel_type

        liters = float(data['liters_sold'])
        unit_price = float(data.get('unit_price', fuel_type.sell_price))
        total = round(liters * unit_price, 2)
        payment_method = data.get('payment_method', 'Cash')

        if liters <= 0:
            raise ValueError('Litirku waa inuu ka weyn yahay eber')

        fleet_profile = None
        if payment_method == 'Credit':
            fleet_id = data.get('fleet_profile_id')
            if not fleet_id:
                raise ValueError('Fleet customer required for credit sales')
            fleet_profile = FleetProfile.query.filter_by(
                id=fleet_id, tenant_id=PetroleumService._tenant_id(), is_active=True
            ).first_or_404()
            if fleet_profile.current_balance + total > fleet_profile.credit_limit:
                raise ValueError(
                    f'Credit limit exceeded. Limit: {fleet_profile.credit_limit}, '
                    f'Balance: {fleet_profile.current_balance}, Sale: {total}'
                )

        invoice_no = data.get('invoice_no') or f'FS-{int(datetime.utcnow().timestamp())}'

        sale = FuelSale(
            invoice_no=invoice_no,
            pump_id=data.get('pump_id'),
            fuel_type_id=fuel_type.id,
            tank_id=tank.id,
            liters_sold=liters,
            unit_price=unit_price,
            total_amount=total,
            payment_method=payment_method,
            customer_id=data.get('customer_id') or (fleet_profile.customer_id if fleet_profile else None),
            fleet_profile_id=fleet_profile.id if fleet_profile else None,
            vehicle_plate=data.get('vehicle_plate'),
            driver_name=data.get('driver_name'),
            meter_before=data.get('meter_before'),
            meter_after=data.get('meter_after'),
            attendant_id=PetroleumService._user_id(),
            branch_id=data.get('branch_id') or tank.branch_id,
            notes=data.get('notes'),
            shift_number=data.get('shift_number') or PetroleumService.detect_shift_number(
                tenant_now(Tenant.query.get(PetroleumService._tenant_id()))
            ),
            tenant_id=PetroleumService._tenant_id(),
            sale_date=tenant_now(Tenant.query.get(PetroleumService._tenant_id())).replace(tzinfo=None)
        )
        db.session.add(sale)
        db.session.flush()

        PetroleumService.update_tank_level(tank, -liters)
        PetroleumService.add_ledger_entry(
            tank, fuel_type.id, 'sale', sale.id, invoice_no,
            0, liters, unit_cost=fuel_type.buy_price,
            notes=f'Sale to {data.get("vehicle_plate") or "walk-in"}'
        )

        if fleet_profile:
            fleet_profile.current_balance = round(fleet_profile.current_balance + total, 2)

        from app.services.accounting_service import AccountingService
        AccountingService.ensure_petroleum_accounts(sale.tenant_id)
        AccountingService.record_fuel_sale(sale, fuel_type)

        log_audit('FUEL_SALE', 'PETROLEUM',
                  f'Sale {invoice_no}: {liters}L {fuel_type.name} = {total}')
        return sale

    @staticmethod
    def delete_sale(sale_id):
        sale = FuelSale.query.filter_by(
            id=sale_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        if sale.is_locked:
            raise ValueError('Iibkan waa la xiray — lama tirtiri karo')

        tank = sale.tank
        PetroleumService.update_tank_level(tank, sale.liters_sold)

        if sale.fleet_profile_id and sale.payment_method == 'Credit':
            sale.fleet_profile.current_balance = round(
                sale.fleet_profile.current_balance - sale.total_amount, 2
            )

        FuelStockLedger.query.filter_by(
            tenant_id=sale.tenant_id, transaction_type='sale', reference_id=sale.id
        ).delete()

        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(sale.invoice_no, sale.tenant_id)

        inv = sale.invoice_no
        db.session.delete(sale)
        log_audit('DELETE', 'PETROLEUM', f'Fuel sale deleted: {inv}')
        return inv

    @staticmethod
    def update_sale(sale_id, data):
        sale = FuelSale.query.filter_by(
            id=sale_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        if sale.is_locked:
            raise ValueError('Iibkan waa la xiray — lama beddeli karo')

        tank = sale.tank
        fuel_type = sale.fuel_type
        old_liters = sale.liters_sold
        old_total = sale.total_amount

        PetroleumService.update_tank_level(tank, old_liters)
        if sale.fleet_profile_id and sale.payment_method == 'Credit':
            sale.fleet_profile.current_balance = round(
                sale.fleet_profile.current_balance - old_total, 2
            )

        new_liters = float(data['liters_sold'])
        new_price = float(data.get('unit_price', sale.unit_price))
        new_total = round(new_liters * new_price, 2)
        if new_liters <= 0:
            raise ValueError('Litirku waa inuu ka weyn yahay eber')

        sale.liters_sold = new_liters
        sale.unit_price = new_price
        sale.total_amount = new_total
        if 'vehicle_plate' in data:
            sale.vehicle_plate = data.get('vehicle_plate') or None
        if 'driver_name' in data:
            sale.driver_name = data.get('driver_name') or None

        PetroleumService.update_tank_level(tank, -new_liters)
        if sale.fleet_profile_id and sale.payment_method == 'Credit':
            sale.fleet_profile.current_balance = round(
                sale.fleet_profile.current_balance + new_total, 2
            )

        FuelStockLedger.query.filter_by(
            tenant_id=sale.tenant_id, transaction_type='sale', reference_id=sale.id
        ).delete()
        PetroleumService.add_ledger_entry(
            tank, fuel_type.id, 'sale', sale.id, sale.invoice_no,
            0, new_liters, unit_cost=fuel_type.buy_price,
            notes=f'Sale updated: {sale.vehicle_plate or "walk-in"}'
        )

        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(sale.invoice_no, sale.tenant_id)
        AccountingService.record_fuel_sale(sale, fuel_type)

        log_audit('UPDATE', 'PETROLEUM',
                  f'Sale {sale.invoice_no} updated: {new_liters}L = {new_total}')
        return sale

    @staticmethod
    def record_delivery(data):
        tank = FuelTank.query.filter_by(
            id=data['tank_id'], tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        fuel_type = FuelType.query.filter_by(
            id=data['fuel_type_id'], tenant_id=PetroleumService._tenant_id()
        ).first_or_404()

        liters = float(data['liters_received'])
        unit_cost = float(data.get('unit_cost', fuel_type.buy_price))
        total_cost = round(liters * unit_cost, 2)

        if liters <= 0:
            raise ValueError('Litirku waa inuu ka weyn yahay eber')

        new_level = (tank.current_level or 0) + liters
        if new_level > tank.capacity_liters:
            raise ValueError(
                f'Tank capacity exceeded. Capacity: {tank.capacity_liters}L, '
                f'Current: {tank.current_level}L, Delivery: {liters}L'
            )

        delivery_no = data.get('delivery_no') or f'FD-{int(datetime.utcnow().timestamp())}'

        vendor_id = data.get('vendor_id') or None
        if vendor_id:
            vendor_id = int(vendor_id)

        delivery = FuelDelivery(
            delivery_no=delivery_no,
            vendor_id=vendor_id,
            purchase_name=(data.get('purchase_name') or '').strip() or None,
            fuel_type_id=fuel_type.id,
            tank_id=tank.id,
            liters_received=liters,
            unit_cost=unit_cost,
            total_cost=total_cost,
            waybill_no=data.get('waybill_no'),
            driver_name=data.get('driver_name'),
            vehicle_no=data.get('vehicle_no'),
            before_dip=data.get('before_dip'),
            after_dip=data.get('after_dip'),
            user_id=PetroleumService._user_id(),
            branch_id=data.get('branch_id') or tank.branch_id,
            notes=data.get('notes'),
            payment_method=data.get('payment_method', 'CREDIT'),
            tenant_id=PetroleumService._tenant_id(),
            delivery_date=tenant_now(Tenant.query.get(PetroleumService._tenant_id())).replace(tzinfo=None)
        )
        db.session.add(delivery)
        db.session.flush()

        PetroleumService.update_tank_level(tank, liters)
        PetroleumService.add_ledger_entry(
            tank, fuel_type.id, 'delivery', delivery.id, delivery_no,
            liters, 0, unit_cost=unit_cost,
            notes=f'Delivery waybill: {data.get("waybill_no") or "N/A"}'
        )

        if data.get('after_dip'):
            tank.last_dip_reading = float(data['after_dip'])
            tank.last_dip_date = datetime.utcnow()

        from app.services.accounting_service import AccountingService
        AccountingService.ensure_petroleum_accounts(delivery.tenant_id)
        AccountingService.record_fuel_delivery(
            delivery, payment_method=data.get('payment_method', 'CREDIT')
        )

        log_audit('FUEL_DELIVERY', 'PETROLEUM',
                  f'Delivery {delivery_no}: {liters}L {fuel_type.name}')
        return delivery

    @staticmethod
    def delete_delivery(delivery_id):
        delivery = FuelDelivery.query.filter_by(
            id=delivery_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        if delivery.is_locked:
            raise ValueError('Soo-dejintan waa la xiray — lama tirtiri karo')

        tank = delivery.tank
        PetroleumService.update_tank_level(tank, -delivery.liters_received)

        FuelStockLedger.query.filter_by(
            tenant_id=delivery.tenant_id, transaction_type='delivery', reference_id=delivery.id
        ).delete()

        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(delivery.delivery_no, delivery.tenant_id)

        ref = delivery.delivery_no
        db.session.delete(delivery)
        log_audit('DELETE', 'PETROLEUM', f'Fuel delivery deleted: {ref}')
        return ref

    @staticmethod
    def update_delivery(delivery_id, data):
        delivery = FuelDelivery.query.filter_by(
            id=delivery_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        if delivery.is_locked:
            raise ValueError('Soo-dejintan waa la xiray — lama beddeli karo')

        tank = delivery.tank
        fuel_type = delivery.fuel_type
        old_liters = delivery.liters_received

        PetroleumService.update_tank_level(tank, -old_liters)

        new_liters = float(data['liters_received'])
        new_cost = float(data.get('unit_cost', delivery.unit_cost))
        new_total = round(new_liters * new_cost, 2)
        if new_liters <= 0:
            raise ValueError('Litirku waa inuu ka weyn yahay eber')

        new_level = (tank.current_level or 0) + new_liters
        if new_level > tank.capacity_liters:
            raise ValueError(
                f'Tankigu buuxay! Awoodda: {tank.capacity_liters}L, '
                f'Hadda: {tank.current_level}L'
            )

        delivery.liters_received = new_liters
        delivery.unit_cost = new_cost
        delivery.total_cost = new_total
        if 'purchase_name' in data:
            delivery.purchase_name = (data.get('purchase_name') or '').strip() or None
        if 'vendor_id' in data:
            vendor_id = data.get('vendor_id') or None
            delivery.vendor_id = int(vendor_id) if vendor_id else None

        PetroleumService.update_tank_level(tank, new_liters)

        FuelStockLedger.query.filter_by(
            tenant_id=delivery.tenant_id, transaction_type='delivery', reference_id=delivery.id
        ).delete()
        PetroleumService.add_ledger_entry(
            tank, fuel_type.id, 'delivery', delivery.id, delivery.delivery_no,
            new_liters, 0, unit_cost=new_cost,
            notes='Soo-dejin la cusboonaysiiyay'
        )

        from app.services.accounting_service import AccountingService
        AccountingService.delete_entries(delivery.delivery_no, delivery.tenant_id)
        AccountingService.record_fuel_delivery(delivery, payment_method='CREDIT')

        log_audit('UPDATE', 'PETROLEUM',
                  f'Delivery {delivery.delivery_no} updated: {new_liters}L = {new_total}')
        return delivery

    @staticmethod
    def record_dip(data):
        tank = FuelTank.query.filter_by(
            id=data['tank_id'], tenant_id=PetroleumService._tenant_id()
        ).first_or_404()

        reading = float(data['reading_liters'])
        book_stock = tank.current_level or 0
        variance = round(reading - book_stock, 2)
        reading_type = data.get('reading_type', 'closing')

        dip = FuelDipReading(
            tank_id=tank.id,
            reading_liters=reading,
            book_stock=book_stock,
            variance=variance,
            reading_type=reading_type,
            notes=data.get('notes'),
            user_id=PetroleumService._user_id(),
            branch_id=tank.branch_id,
            tenant_id=PetroleumService._tenant_id(),
            reading_date=tenant_now(Tenant.query.get(PetroleumService._tenant_id())).replace(tzinfo=None)
        )
        db.session.add(dip)
        db.session.flush()

        tank.last_dip_reading = reading
        tank.last_dip_date = datetime.utcnow()

        if abs(variance) > 0.01 and data.get('apply_variance'):
            PetroleumService.update_tank_level(tank, variance)
            PetroleumService.add_ledger_entry(
                tank, tank.fuel_type_id, 'dip_adjustment', dip.id,
                f'DIP-{dip.id}',
                max(variance, 0), max(-variance, 0),
                notes=f'Dip variance adjustment: {variance}L'
            )
            from app.services.accounting_service import AccountingService
            fuel_type = FuelType.query.get(tank.fuel_type_id)
            AccountingService.ensure_petroleum_accounts(dip.tenant_id)
            AccountingService.record_fuel_dip_variance(dip, tank, fuel_type, variance)

        log_audit('FUEL_DIP', 'PETROLEUM',
                  f'Dip {reading_type} on {tank.name}: {reading}L (variance {variance}L)')
        return dip

    @staticmethod
    def change_price(fuel_type_id, new_buy, new_sell, reason=None, name=None, code=None, color_code=None):
        fuel_type = FuelType.query.filter_by(
            id=fuel_type_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()

        history = FuelPriceHistory(
            fuel_type_id=fuel_type.id,
            old_buy_price=fuel_type.buy_price,
            new_buy_price=new_buy,
            old_sell_price=fuel_type.sell_price,
            new_sell_price=new_sell,
            reason=reason,
            changed_by=PetroleumService._user_id(),
            tenant_id=PetroleumService._tenant_id()
        )
        db.session.add(history)

        old_sell = fuel_type.sell_price
        fuel_type.buy_price = new_buy
        fuel_type.sell_price = new_sell
        
        if name: fuel_type.name = name
        if code: fuel_type.code = code
        if color_code: fuel_type.color_code = color_code

        log_audit('FUEL_PRICE_CHANGE', 'PETROLEUM',
                  f'{fuel_type.name}: sell {old_sell} -> {new_sell}')
        return history

    @staticmethod
    def _admin_user_id(tenant_id):
        user = User.query.filter_by(tenant_id=tenant_id, role='admin').first()
        if not user:
            user = User.query.filter_by(tenant_id=tenant_id).first()
        if not user:
            raise ValueError(f'No user found for tenant {tenant_id}')
        return user.id

    @staticmethod
    def _tanks_requiring_dip(tanks, sales=None, deliveries=None):
        """Tanks that need opening/closing dips — matches morning automation (fuel in tank or activity)."""
        tank_ids = {s.tank_id for s in (sales or []) if s.tank_id}
        tank_ids.update(d.tank_id for d in (deliveries or []) if d.tank_id)
        if tank_ids:
            return [t for t in tanks if t.id in tank_ids]
        return [t for t in tanks if (t.current_level or 0) > 0.01]

    @staticmethod
    def get_day_summary(target_date=None, branch_id=None, tenant_id=None):
        tenant = Tenant.query.get(tenant_id or PetroleumService._tenant_id())
        target_date = target_date or tenant_today(tenant)
        tenant_id = tenant.id
        start_utc, end_utc = local_day_utc_bounds(target_date, tenant)

        sales_q = FuelSale.query.filter_by(tenant_id=tenant_id).filter(
            FuelSale.sale_date >= start_utc,
            FuelSale.sale_date <= end_utc
        )
        deliveries_q = FuelDelivery.query.filter_by(tenant_id=tenant_id).filter(
            FuelDelivery.delivery_date >= start_utc,
            FuelDelivery.delivery_date <= end_utc
        )
        dips_q = FuelDipReading.query.filter_by(tenant_id=tenant_id).filter(
            FuelDipReading.reading_date >= start_utc,
            FuelDipReading.reading_date <= end_utc
        )

        if branch_id:
            sales_q = sales_q.filter_by(branch_id=branch_id)
            deliveries_q = deliveries_q.filter_by(branch_id=branch_id)
            dips_q = dips_q.filter(FuelDipReading.branch_id == branch_id)

        sales = sales_q.all()
        deliveries = deliveries_q.all()
        dips = dips_q.all()

        tanks = FuelTank.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        if branch_id:
            tanks = [t for t in tanks if t.branch_id == branch_id]

        opening_dips = [d for d in dips if d.reading_type == 'opening']
        closing_dips = [d for d in dips if d.reading_type == 'closing']
        tanks_requiring_dip = PetroleumService._tanks_requiring_dip(tanks, sales, deliveries)
        opening_count = sum(1 for t in tanks_requiring_dip if any(d.tank_id == t.id for d in opening_dips))
        closing_count = sum(1 for t in tanks_requiring_dip if any(d.tank_id == t.id for d in closing_dips))

        return {
            'date': target_date,
            'sales': sales,
            'deliveries': deliveries,
            'dips': dips,
            'opening_dips': opening_dips,
            'closing_dips': closing_dips,
            'tanks': tanks,
            'tanks_requiring_dip': tanks_requiring_dip,
            'total_sales_liters': sum(s.liters_sold for s in sales),
            'total_sales_amount': sum(s.total_amount for s in sales),
            'total_deliveries_liters': sum(d.liters_received for d in deliveries),
            'total_variance': sum(abs(d.variance) for d in dips),
            'has_opening_dip': opening_count >= len(tanks_requiring_dip) if tanks_requiring_dip else True,
            'has_closing_dip': closing_count >= len(tanks_requiring_dip) if tanks_requiring_dip else True,
        }

    @staticmethod
    def close_day(target_date=None, branch_id=None, notes=None):
        tenant = Tenant.query.get(PetroleumService._tenant_id())
        target_date = target_date or tenant_today(tenant)
        summary = PetroleumService.get_day_summary(target_date, branch_id)

        if tenant.petroleum_require_daily_dip:
            if summary['tanks'] and not summary['has_opening_dip']:
                raise ValueError('Opening dip readings required for all tanks before day close')
            if summary['tanks'] and not summary['has_closing_dip']:
                raise ValueError('Closing dip readings required for all tanks before day close')

        existing = FuelDayClose.query.filter_by(
            tenant_id=PetroleumService._tenant_id(),
            close_date=target_date,
            branch_id=branch_id
        ).first()
        if existing:
            raise ValueError(f'Day {target_date} is already closed')

        for sale in summary['sales']:
            sale.is_locked = True
        for delivery in summary['deliveries']:
            delivery.is_locked = True

        day_close = FuelDayClose(
            close_date=target_date,
            branch_id=branch_id,
            total_sales_liters=summary['total_sales_liters'],
            total_sales_amount=summary['total_sales_amount'],
            total_deliveries_liters=summary['total_deliveries_liters'],
            total_variance=summary['total_variance'],
            status='closed',
            notes=notes,
            closed_by=PetroleumService._user_id(),
            tenant_id=PetroleumService._tenant_id()
        )
        db.session.add(day_close)

        log_audit('FUEL_DAY_CLOSE', 'PETROLEUM',
                  f'Day closed {target_date}: {summary["total_sales_liters"]}L sold')
        return day_close

    @staticmethod
    def close_day_system(tenant_id, target_date, user_id, notes=None, auto=False):
        tenant = Tenant.query.get(tenant_id)
        summary = PetroleumService.get_day_summary(target_date, tenant_id=tenant_id)

        if not auto and tenant.petroleum_require_daily_dip:
            if summary['tanks'] and not summary['has_opening_dip']:
                raise ValueError('Opening dip readings required for all tanks before day close')
            if summary['tanks'] and not summary['has_closing_dip']:
                raise ValueError('Closing dip readings required for all tanks before day close')

        existing = FuelDayClose.query.filter_by(
            tenant_id=tenant_id, close_date=target_date, branch_id=None
        ).first()
        if existing:
            return existing

        for sale in summary['sales']:
            sale.is_locked = True
        for delivery in summary['deliveries']:
            delivery.is_locked = True

        day_close = FuelDayClose(
            close_date=target_date,
            branch_id=None,
            total_sales_liters=summary['total_sales_liters'],
            total_sales_amount=summary['total_sales_amount'],
            total_deliveries_liters=summary['total_deliveries_liters'],
            total_variance=summary['total_variance'],
            status='closed',
            notes=notes or 'Automatic',
            closed_by=user_id,
            tenant_id=tenant_id
        )
        db.session.add(day_close)
        log_audit('FUEL_DAY_CLOSE', 'PETROLEUM',
                  f'Auto day closed {target_date}: {summary["total_sales_liters"]}L sold')
        return day_close

    @staticmethod
    def record_dip_system(tenant_id, tank_id, reading_liters, reading_type='opening',
                          user_id=None, notes=None, apply_variance=False, reading_date=None):
        tank = FuelTank.query.filter_by(id=tank_id, tenant_id=tenant_id).first_or_404()
        tenant = Tenant.query.get(tenant_id)
        user_id = user_id or PetroleumService._admin_user_id(tenant_id)

        reading = float(reading_liters)
        book_stock = tank.current_level or 0
        variance = round(reading - book_stock, 2)
        if reading_date is None:
            reading_date = tenant_now(tenant).replace(tzinfo=None)

        dip = FuelDipReading(
            tank_id=tank.id,
            reading_liters=reading,
            book_stock=book_stock,
            variance=variance,
            reading_type=reading_type,
            notes=notes,
            user_id=user_id,
            branch_id=tank.branch_id,
            tenant_id=tenant_id,
            reading_date=reading_date
        )
        db.session.add(dip)
        db.session.flush()

        tank.last_dip_reading = reading
        tank.last_dip_date = reading_date

        if abs(variance) > 0.01 and apply_variance:
            PetroleumService.update_tank_level(tank, variance)
            PetroleumService.add_ledger_entry(
                tank, tank.fuel_type_id, 'dip_adjustment', dip.id,
                f'DIP-{dip.id}',
                max(variance, 0), max(-variance, 0),
                notes=f'Dip variance adjustment: {variance}L'
            )
            from app.services.accounting_service import AccountingService
            fuel_type = FuelType.query.get(tank.fuel_type_id)
            AccountingService.ensure_petroleum_accounts(tenant_id)
            AccountingService.record_fuel_dip_variance(dip, tank, fuel_type, variance)

        log_audit('FUEL_DIP', 'PETROLEUM',
                  f'Auto dip {reading_type} on {tank.name}: {reading}L')
        return dip

    @staticmethod
    def run_morning_automation(tenant_id, force=False):
        """Subax 6AM: xir maalintii shalay + qiyaas subaxnimo maanta."""
        from app.services.petroleum_scheduler import is_morning_automatic

        tenant = Tenant.query.get(tenant_id)
        if not tenant or not tenant.module_petroleum:
            return {'skipped': True, 'reason': 'no_module'}
        if not force and not is_morning_automatic(tenant):
            return {'skipped': True, 'reason': 'manual_mode'}
        if not PetroleumService.is_setup_complete(tenant_id):
            return {'skipped': True, 'reason': 'no_setup'}

        today = tenant_today(tenant)
        yesterday = today - timedelta(days=1)
        admin_id = PetroleumService._admin_user_id(tenant_id)
        tanks = FuelTank.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        tanks_with_fuel = [t for t in tanks if (t.current_level or 0) > 0.01]

        if not tanks_with_fuel:
            return {'skipped': True, 'reason': 'empty_tanks'}

        results = {'closing_dips': 0, 'day_closed': False, 'opening_dips': 0, 'date': str(today)}

        # 1. Xir maalintii shalay
        if not FuelDayClose.query.filter_by(tenant_id=tenant_id, close_date=yesterday).first():
            summary_y = PetroleumService.get_day_summary(yesterday, tenant_id=tenant_id)
            had_activity = (
                summary_y['total_sales_liters'] > 0 or
                summary_y['total_deliveries_liters'] > 0 or
                len(summary_y['dips']) > 0
            )
            if had_activity:
                for tank in tanks_with_fuel:
                    if not any(d.tank_id == tank.id for d in summary_y['closing_dips']):
                        PetroleumService.record_dip_system(
                            tenant_id, tank.id, tank.current_level,
                            reading_type='closing', user_id=admin_id,
                            notes='Automatic — subax 6AM',
                            reading_date=end_of_local_day_utc(yesterday, tenant)
                        )
                        results['closing_dips'] += 1
                PetroleumService.close_day_system(
                    tenant_id, yesterday, admin_id,
                    notes='Automatic — subax 6AM', auto=True
                )
                results['day_closed'] = True

        # 2. Qiyaas subaxnimo maanta
        summary_t = PetroleumService.get_day_summary(today, tenant_id=tenant_id)
        for tank in tanks_with_fuel:
            if not any(d.tank_id == tank.id for d in summary_t['opening_dips']):
                PetroleumService.record_dip_system(
                    tenant_id, tank.id, tank.current_level,
                    reading_type='opening', user_id=admin_id,
                    notes='Automatic — subax 6AM'
                )
                results['opening_dips'] += 1

        return results

    @staticmethod
    def seed_default_fuel_types(tenant_id, custom_types=None):
        if FuelType.query.filter_by(tenant_id=tenant_id).first():
            return
        defaults = custom_types or [
            ('Petrol', 'PET', '#ef4444', 1.20, 1.45),
            ('Diesel', 'DSL', '#f59e0b', 1.10, 1.35),
            ('Kerosene', 'KER', '#3b82f6', 0.95, 1.15),
        ]
        for name, code, color, buy, sell in defaults:
            db.session.add(FuelType(
                name=name, code=code, color_code=color,
                buy_price=buy, sell_price=sell, tenant_id=tenant_id
            ))

    @staticmethod
    def record_fleet_payment(profile, amount, payment_method='Cash', discount=0.0):
        profile.current_balance = round(profile.current_balance - (amount + discount), 2)
        from app.services.accounting_service import AccountingService
        AccountingService.ensure_petroleum_accounts(profile.tenant_id)
        AccountingService.record_fleet_payment(profile, amount, payment_method, discount)
        log_audit('FLEET_PAYMENT', 'PETROLEUM',
                  f'Fleet payment {amount} (Discount: {discount}) from customer {profile.customer_id}')

    @staticmethod
    def run_initial_setup(tenant_id, data):
        """
        One-shot setup: fuel types, chart accounts, tanks, pumps, fleet, opening stock.
        data keys: tanks[], pumps[], fleet[], branch_id
        """
        from app.models import Branch, Customer
        from app.services.accounting_service import AccountingService

        PetroleumService.seed_default_fuel_types(tenant_id)
        db.session.flush()
        AccountingService.ensure_petroleum_accounts(tenant_id)

        fuel_types = {ft.code: ft for ft in FuelType.query.filter_by(tenant_id=tenant_id).all()}
        branch_id = data.get('branch_id')
        if branch_id:
            branch_id = int(branch_id)
        elif Branch.query.filter_by(tenant_id=tenant_id).first():
            branch_id = Branch.query.filter_by(tenant_id=tenant_id).first().id

        tank_map = {}
        for i, t in enumerate(data.get('tanks', [])):
            ft = fuel_types.get(t.get('fuel_code', 'DSL')) or list(fuel_types.values())[0]
            tank = FuelTank(
                name=t.get('name', f'Tank {i + 1} - {ft.name}'),
                fuel_type_id=ft.id,
                branch_id=branch_id,
                capacity_liters=float(t.get('capacity', 50000)),
                current_level=float(t.get('opening_level', 0)),
                min_alert_level=float(t.get('min_alert', 5000)),
                tenant_id=tenant_id
            )
            db.session.add(tank)
            db.session.flush()
            tank_map[t.get('key', str(i))] = tank

            opening = float(t.get('opening_level', 0))
            if opening > 0:
                PetroleumService.add_ledger_entry(
                    tank, ft.id, 'opening_stock', tank.id, f'OPEN-{tank.id}',
                    opening, 0, unit_cost=ft.buy_price,
                    notes='Initial opening stock'
                )
                AccountingService.record_fuel_opening_stock(
                    tenant_id, tank.name, opening, ft.buy_price
                )

        for i, p in enumerate(data.get('pumps', [])):
            tank = tank_map.get(p.get('tank_key'))
            if not tank:
                tank = list(tank_map.values())[0] if tank_map else None
            if not tank:
                continue
            ft = FuelType.query.get(tank.fuel_type_id)
            db.session.add(FuelPump(
                pump_number=p.get('number', f'Pump {i + 1}'),
                fuel_type_id=ft.id,
                tank_id=tank.id,
                branch_id=branch_id,
                tenant_id=tenant_id
            ))

        for f in data.get('fleet', []):
            customer_id = f.get('customer_id')
            if not customer_id and f.get('customer_name'):
                cust = Customer(
                    name=f['customer_name'],
                    phone=f.get('phone'),
                    tenant_id=tenant_id
                )
                db.session.add(cust)
                db.session.flush()
                customer_id = cust.id
            if not customer_id:
                continue
            if FleetProfile.query.filter_by(customer_id=customer_id, tenant_id=tenant_id).first():
                continue
            db.session.add(FleetProfile(
                customer_id=int(customer_id),
                fleet_code=f.get('fleet_code', f'FLT-{customer_id}'),
                credit_limit=float(f.get('credit_limit', 50000)),
                payment_terms_days=int(f.get('payment_terms', 30)),
                tenant_id=tenant_id
            ))

        log_audit('PETROLEUM_SETUP', 'PETROLEUM',
                  f'Initial setup: {len(tank_map)} tanks, {len(data.get("pumps", []))} pumps')
        return {'tanks': len(tank_map), 'pumps': len(data.get('pumps', [])),
                'fleet': len(data.get('fleet', []))}

    @staticmethod
    def is_setup_complete(tenant_id):
        return (
            FuelType.query.filter_by(tenant_id=tenant_id).count() > 0 and
            FuelTank.query.filter_by(tenant_id=tenant_id, is_active=True).count() > 0
        )

    @staticmethod
    def get_shift_config(tenant):
        return {
            1: {
                'number': 1,
                'name': tenant.petroleum_shift1_name or 'Saaka (7AM-5PM)',
                'attendant': tenant.petroleum_shift1_attendant or '',
                'start_hour': tenant.petroleum_shift1_start_hour if tenant.petroleum_shift1_start_hour is not None else 7,
                'end_hour': tenant.petroleum_shift1_end_hour if tenant.petroleum_shift1_end_hour is not None else 17,
            },
            2: {
                'number': 2,
                'name': tenant.petroleum_shift2_name or 'Habeen (5PM-7AM)',
                'attendant': tenant.petroleum_shift2_attendant or '',
                'start_hour': tenant.petroleum_shift2_start_hour if tenant.petroleum_shift2_start_hour is not None else 17,
                'end_hour': tenant.petroleum_shift2_end_hour if tenant.petroleum_shift2_end_hour is not None else 7,
            },
        }

    @staticmethod
    def get_shift_bounds(target_date, shift_number, tenant):
        tz = get_tenant_timezone(tenant)
        cfg = PetroleumService.get_shift_config(tenant)[shift_number]
        if shift_number == 1:
            start_local = datetime.combine(target_date, time(cfg['start_hour'], 0)).replace(tzinfo=tz)
            end_local = datetime.combine(target_date, time(cfg['end_hour'], 0)).replace(tzinfo=tz)
        else:
            start_local = datetime.combine(target_date, time(cfg['start_hour'], 0)).replace(tzinfo=tz)
            end_local = datetime.combine(
                target_date + timedelta(days=1), time(cfg['end_hour'], 0)
            ).replace(tzinfo=tz)
        return (
            local_datetime_to_utc_naive(start_local),
            local_datetime_to_utc_naive(end_local),
        )

    @staticmethod
    def get_business_day_bounds(target_date, tenant):
        """Maalinta ganacsiga: shift1 bilow ilaa shift2 dhamaad."""
        start_utc, _ = PetroleumService.get_shift_bounds(target_date, 1, tenant)
        _, end_utc = PetroleumService.get_shift_bounds(target_date, 2, tenant)
        return start_utc, end_utc

    @staticmethod
    def detect_shift_number(local_dt, tenant=None):
        tenant = tenant or Tenant.query.get(PetroleumService._tenant_id())
        if hasattr(local_dt, 'tzinfo') and local_dt.tzinfo is not None:
            local_dt = local_dt.astimezone(get_tenant_timezone(tenant)).replace(tzinfo=None)
        cfg = PetroleumService.get_shift_config(tenant)[1]
        hour = local_dt.hour
        if cfg['start_hour'] <= hour < cfg['end_hour']:
            return 1
        return 2

    @staticmethod
    def get_business_date(local_dt, tenant=None):
        tenant = tenant or Tenant.query.get(PetroleumService._tenant_id())
        if hasattr(local_dt, 'tzinfo') and local_dt.tzinfo is not None:
            local_dt = local_dt.astimezone(get_tenant_timezone(tenant)).replace(tzinfo=None)
        s2_end = PetroleumService.get_shift_config(tenant)[2]['end_hour']
        if local_dt.hour < s2_end:
            return local_dt.date() - timedelta(days=1)
        return local_dt.date()

    @staticmethod
    def log_pump_shift_meter(pump_id, log_date, shift_number, opening_meter=None, closing_meter=None):
        pump = FuelPump.query.filter_by(
            id=pump_id, tenant_id=PetroleumService._tenant_id()
        ).first_or_404()
        existing = FuelPumpShiftLog.query.filter_by(
            pump_id=pump.id, log_date=log_date, shift_number=shift_number,
            tenant_id=PetroleumService._tenant_id()
        ).first()
        if existing:
            if opening_meter is not None:
                existing.opening_meter = float(opening_meter)
            if closing_meter is not None:
                existing.closing_meter = float(closing_meter)
        else:
            existing = FuelPumpShiftLog(
                pump_id=pump.id,
                log_date=log_date,
                shift_number=shift_number,
                opening_meter=float(opening_meter) if opening_meter is not None else None,
                closing_meter=float(closing_meter) if closing_meter is not None else None,
                user_id=PetroleumService._user_id(),
                tenant_id=PetroleumService._tenant_id(),
            )
            db.session.add(existing)
        return existing

    @staticmethod
    def _classify_payment_method(method):
        m = (method or 'Cash').strip().lower()
        if m == 'credit':
            return 'credit'
        if 'evc' in m:
            return 'evc'
        if 'dahab' in m or 'edahab' in m:
            return 'edahab'
        if m in ('cash', 'caddaan'):
            return 'cash'
        return 'other'

    @staticmethod
    def _build_shift_pump_rows(pumps, sales, target_date, shift_number, tenant_id, tenant):
        sales_by_pump = {}
        for s in sales:
            if s.pump_id:
                sales_by_pump.setdefault(s.pump_id, []).append(s)

        rows = []
        has_meter = False
        for pump in pumps:
            log = FuelPumpShiftLog.query.filter_by(
                pump_id=pump.id, log_date=target_date, shift_number=shift_number,
                tenant_id=tenant_id
            ).first()
            opening = log.opening_meter if log and log.opening_meter is not None else None
            closing = log.closing_meter if log and log.closing_meter is not None else None
            unit_price = pump.fuel_type.sell_price if pump.fuel_type else 0

            if opening is None and shift_number == 2:
                prev = FuelPumpShiftLog.query.filter_by(
                    pump_id=pump.id, log_date=target_date, shift_number=1, tenant_id=tenant_id
                ).first()
                if prev and prev.closing_meter is not None:
                    opening = prev.closing_meter

            if opening is not None and closing is not None:
                liters = round(closing - opening, 2)
                amount = round(liters * unit_price, 3)
                source = 'meter'
                has_meter = True
            else:
                pump_sales = sales_by_pump.get(pump.id, [])
                liters = round(sum(s.liters_sold for s in pump_sales), 2)
                amount = round(sum(s.total_amount for s in pump_sales), 3)
                if pump_sales:
                    unit_price = pump_sales[0].unit_price
                source = 'sales' if pump_sales else 'empty'

            rows.append({
                'pump_number': pump.pump_number,
                'fuel_name': pump.fuel_type.name if pump.fuel_type else '—',
                'opening_meter': opening,
                'closing_meter': closing,
                'liters_sold': liters,
                'unit_price': unit_price,
                'total_amount': amount,
                'source': source,
            })
        return rows, has_meter

    @staticmethod
    def _build_shift_payments(sales):
        payments = {'cash': 0.0, 'evc': 0.0, 'edahab': 0.0, 'credit': 0.0, 'other': 0.0, 'discount': 0.0}
        for s in sales:
            bucket = PetroleumService._classify_payment_method(s.payment_method)
            payments[bucket] = round(payments[bucket] + s.total_amount, 3)
        return payments

    @staticmethod
    def _build_shift_debts(sales):
        debt_map = {}
        for s in sales:
            if PetroleumService._classify_payment_method(s.payment_method) != 'credit':
                continue
            name = '—'
            if s.fleet_profile and s.fleet_profile.customer:
                name = s.fleet_profile.customer.name
            elif s.customer:
                name = s.customer.name
            if name not in debt_map:
                debt_map[name] = {'name': name, 'liters': 0.0, 'unit_price': s.unit_price, 'total': 0.0}
            debt_map[name]['liters'] = round(debt_map[name]['liters'] + s.liters_sold, 2)
            debt_map[name]['total'] = round(debt_map[name]['total'] + s.total_amount, 3)
        return sorted(debt_map.values(), key=lambda d: d['total'], reverse=True)

    @staticmethod
    def get_daily_closing_report(target_date=None, branch_id=None, tenant_id=None):
        """Warbixin maalinle ah — 2 shift, pombada, lacag bixinta, deynta."""
        tenant = Tenant.query.get(tenant_id or PetroleumService._tenant_id())
        target_date = target_date or tenant_today(tenant)
        tenant_id = tenant.id
        shift_cfg = PetroleumService.get_shift_config(tenant)

        pumps_q = FuelPump.query.filter_by(tenant_id=tenant_id, is_active=True)
        if branch_id:
            pumps_q = pumps_q.filter_by(branch_id=branch_id)
        pumps = pumps_q.order_by(FuelPump.pump_number).all()

        shifts = []
        all_sales = []
        has_meter_data = False

        for sn in (1, 2):
            start_utc, end_utc = PetroleumService.get_shift_bounds(target_date, sn, tenant)
            sales_q = FuelSale.query.filter_by(tenant_id=tenant_id).filter(
                FuelSale.sale_date >= start_utc,
                FuelSale.sale_date < end_utc,
            )
            if branch_id:
                sales_q = sales_q.filter_by(branch_id=branch_id)
            shift_sales = sales_q.all()

            pump_rows, shift_meter = PetroleumService._build_shift_pump_rows(
                pumps, shift_sales, target_date, sn, tenant_id, tenant
            )
            payments = PetroleumService._build_shift_payments(shift_sales)
            debts = PetroleumService._build_shift_debts(shift_sales)
            has_meter_data = has_meter_data or shift_meter
            all_sales.extend(shift_sales)

            attendant_names = set()
            for s in shift_sales:
                if s.attendant:
                    attendant_names.add(s.attendant.username)
            
            if not attendant_names:
                from app.models import FuelPumpShiftLog
                logs = FuelPumpShiftLog.query.filter_by(
                    log_date=target_date, shift_number=sn, tenant_id=tenant_id
                ).all()
                for lg in logs:
                    if lg.user:
                        attendant_names.add(lg.user.username)
                        
            dynamic_attendant = ", ".join(sorted(attendant_names)) if attendant_names else ""

            cfg = shift_cfg[sn]
            shifts.append({
                'number': sn,
                'name': cfg['name'],
                'attendant': dynamic_attendant,
                'time_label': f"{cfg['start_hour']:02d}:00 – {cfg['end_hour']:02d}:00",
                'pumps': pump_rows,
                'pump_totals': {
                    'liters': round(sum(r['liters_sold'] for r in pump_rows), 2),
                    'amount': round(sum(r['total_amount'] for r in pump_rows), 3),
                },
                'payments': payments,
                'debts': debts,
                'sales_count': len(shift_sales),
            })

        payments_total = {'cash': 0.0, 'evc': 0.0, 'edahab': 0.0, 'credit': 0.0, 'other': 0.0, 'discount': 0.0}
        for sh in shifts:
            for k in payments_total:
                payments_total[k] = round(payments_total[k] + sh['payments'][k], 3)

        total_fuel = round(sum(sh['pump_totals']['liters'] for sh in shifts), 2)
        total_revenue = round(sum(sh['pump_totals']['amount'] for sh in shifts), 3)
        if total_revenue == 0 and all_sales:
            total_fuel = round(sum(s.liters_sold for s in all_sales), 2)
            total_revenue = round(sum(s.total_amount for s in all_sales), 3)

        total_collected = round(
            payments_total['cash'] + payments_total['evc'] + payments_total['edahab'] + payments_total['other'], 3
        )
        closed = FuelDayClose.query.filter_by(
            tenant_id=tenant_id, close_date=target_date, branch_id=branch_id
        ).first()

        all_debts = PetroleumService._build_shift_debts(
            [s for s in all_sales if PetroleumService._classify_payment_method(s.payment_method) == 'credit']
        )

        # Deliveries (Purchases) for the day
        from app.models import FuelDelivery
        deliveries = FuelDelivery.query.filter_by(tenant_id=tenant_id).filter(
            db.func.date(FuelDelivery.delivery_date) == target_date
        ).all()
        
        del_totals = {'paid': 0.0, 'credit': 0.0, 'liters': 0.0}
        for d in deliveries:
            del_totals['liters'] += d.liters_received
            if d.payment_method == 'CASH':
                del_totals['paid'] += d.total_cost
            else:
                del_totals['credit'] += d.total_cost

        return {
            'date': target_date,
            'shifts': shifts,
            'shift_config': shift_cfg,
            'payments': payments_total,
            'debts': all_debts,
            'deliveries': deliveries,
            'delivery_totals': del_totals,
            'totals': {
                'total_debt': payments_total['credit'],
                'total_collected': total_collected,
                'total_fuel': total_fuel,
                'total_revenue': total_revenue,
            },
            'is_closed': closed is not None,
            'closed_at': closed.created_at if closed else None,
            'has_meter_data': has_meter_data,
            'sales_count': len(all_sales),
            'full_report': True,
        }
