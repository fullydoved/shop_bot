"""Background scheduler for checking reminders."""

import logging
import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler | None = None


def check_reminders_job():
    """Job that runs periodically to check for due reminders."""
    # Import here to avoid circular imports and ensure Django is ready
    from .services import check_and_trigger_reminders, cleanup_old_reminders

    try:
        triggered = check_and_trigger_reminders()
        if triggered:
            titles = [r.title for r in triggered]
            logger.info(f"Triggered {len(triggered)} reminder(s): {titles}")

        # Occasionally clean up old reminders (every ~100 checks)
        if random.random() < 0.01:
            deleted = cleanup_old_reminders()
            if deleted:
                logger.info(f"Cleaned up {deleted} old reminder(s)")

    except Exception as e:
        logger.error(f"Error checking reminders: {e}")


def start_scheduler():
    """Start the background scheduler."""
    global _scheduler

    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return

    _scheduler = BackgroundScheduler()

    # Check reminders every 30 seconds
    _scheduler.add_job(
        check_reminders_job,
        trigger=IntervalTrigger(seconds=30),
        id='check_reminders',
        name='Check for due reminders',
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Reminder scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler

    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Reminder scheduler stopped")


def is_scheduler_running() -> bool:
    """Check if scheduler is running."""
    return _scheduler is not None and _scheduler.running
