"""Background scheduler: petroleum morning automation (tenant local time)."""
import threading
import time
import logging
from datetime import datetime

from app.utils.datetime_utils import get_tenant_timezone, tenant_today

logger = logging.getLogger(__name__)

_last_run = {}  # (tenant_id, date) -> True
_scheduler_started = False

MORNING_MODE_AUTOMATIC = 'automatic'
MORNING_MODE_MANUAL = 'manual'
MORNING_WINDOW_MINUTES = 30


def is_morning_automatic(tenant):
    """True when tenant uses scheduled morning automation (not manual dips)."""
    mode = getattr(tenant, 'petroleum_morning_mode', None)
    if mode in (MORNING_MODE_AUTOMATIC, MORNING_MODE_MANUAL):
        return mode == MORNING_MODE_AUTOMATIC
    return getattr(tenant, 'petroleum_auto_morning_dip', True) is not False


def _in_morning_window(now, run_hour):
    """Run only within [run_hour:00, run_hour:30] local time."""
    if now.hour < run_hour:
        return False
    if now.hour > run_hour:
        return False
    return now.minute <= MORNING_WINDOW_MINUTES


def check_morning_jobs(app):
    """Run morning automation for tenants in automatic mode within the morning window."""
    from app.models import Tenant
    from app.services.petroleum_service import PetroleumService

    tenants = Tenant.query.filter_by(module_petroleum=True).all()
    for tenant in tenants:
        if not is_morning_automatic(tenant):
            continue
        tz = get_tenant_timezone(tenant)
        now = datetime.now(tz)
        run_hour = getattr(tenant, 'petroleum_morning_auto_hour', None) or 6
        today = tenant_today(tenant)
        key = (tenant.id, today)

        if not _in_morning_window(now, run_hour) or key in _last_run:
            continue

        try:
            result = PetroleumService.run_morning_automation(tenant.id)
            from app import db
            db.session.commit()
            _last_run[key] = True
            if not result.get('skipped'):
                logger.info('Petroleum morning automation tenant=%s: %s', tenant.id, result)
        except Exception:
            from app import db
            db.session.rollback()
            logger.exception('Petroleum morning automation failed tenant=%s', tenant.id)


def _scheduler_loop(app):
    with app.app_context():
        while True:
            try:
                check_morning_jobs(app)
            except Exception:
                logger.exception('Petroleum scheduler tick failed')
            time.sleep(60)


def start_petroleum_scheduler(app):
    global _scheduler_started
    if _scheduler_started or not app.config.get('PETROLEUM_SCHEDULER_ENABLED', True):
        return
    _scheduler_started = True
    t = threading.Thread(target=_scheduler_loop, args=(app,), daemon=True, name='petroleum-scheduler')
    t.start()
    logger.info('Petroleum morning scheduler started (checks every 60s)')
