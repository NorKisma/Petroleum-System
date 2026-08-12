"""Tenant-local date/time helpers for consistent daily summaries."""
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_TZ_ALIASES = {
    'Africa/Muqdisho': 'Africa/Mogadishu',
}


def get_tenant_timezone(tenant):
    tz_name = 'Africa/Mogadishu'
    if tenant and getattr(tenant, 'timezone', None):
        tz_name = _TZ_ALIASES.get(tenant.timezone, tenant.timezone)
    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo('UTC')


def tenant_today(tenant):
    return datetime.now(get_tenant_timezone(tenant)).date()


def tenant_now(tenant):
    return datetime.now(get_tenant_timezone(tenant))


def local_day_utc_bounds(target_date, tenant):
    """Return (start_utc, end_utc) naive UTC datetimes for a tenant-local calendar day."""
    tz = get_tenant_timezone(tenant)
    start_local = datetime.combine(target_date, time.min).replace(tzinfo=tz)
    end_local = datetime.combine(target_date, time.max).replace(tzinfo=tz)
    utc = ZoneInfo('UTC')
    start_utc = start_local.astimezone(utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(utc).replace(tzinfo=None)
    return start_utc, end_utc


def end_of_local_day_utc(target_date, tenant):
    """Naive UTC datetime for 23:59:59 on a tenant-local calendar day."""
    tz = get_tenant_timezone(tenant)
    end_local = datetime.combine(target_date, time(23, 59, 59)).replace(tzinfo=tz)
    return end_local.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)


def local_datetime_to_utc_naive(local_dt):
    """Convert timezone-aware local datetime to naive UTC."""
    return local_dt.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)


def utc_naive_to_local(utc_dt, tenant):
    """Convert naive UTC datetime to tenant-local aware datetime."""
    tz = get_tenant_timezone(tenant)
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo('UTC'))
    return utc_dt.astimezone(tz)
