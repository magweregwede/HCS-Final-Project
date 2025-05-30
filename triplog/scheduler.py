import os
import atexit
import matplotlib
# Set matplotlib to use non-GUI backend before any other matplotlib imports
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def run_monthly_report():
    """Function to run monthly report"""
    try:
        logger.info("Running monthly report job...")
        # Ensure matplotlib uses Agg backend in this thread
        matplotlib.use('Agg')
        call_command('send_monthly_report', '--force')
        logger.info("Monthly report job completed successfully")
    except Exception as e:
        logger.error(f"Monthly report job failed: {e}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Test job - every 2 minutes
    scheduler.add_job(
        func=run_monthly_report,
        trigger="interval",
        minutes=2,
        id='test_monthly_report'
    )
    
    # Production job - 25th of every month at 9 AM
    # scheduler.add_job(
    #     func=run_monthly_report,
    #     trigger="cron",
    #     day=25,
    #     hour=9,
    #     minute=0,
    #     id='monthly_report'
    # )
    
    scheduler.start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info("Scheduler started successfully")
    
    return scheduler