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

def export_historical_stats():
    """Function to export historical statistics"""
    try:
        logger.info("Running export historical stats job...")
        call_command('export_hist_stats')
        logger.info("Export historical stats job completed successfully")
    except Exception as e:
        logger.error(f"Export historical stats job failed: {e}")

def update_leaderboard():
    """Function to update driver leaderboard"""
    try:
        logger.info("Running update leaderboard job...")
        call_command('update_leaderboard')
        logger.info("Update leaderboard job completed successfully")
    except Exception as e:
        logger.error(f"Update leaderboard job failed: {e}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Test job - every 2 minutes
    scheduler.add_job(
        func=run_monthly_report,
        trigger="interval",
        # minutes=2,
        hours=1,
        id='test_monthly_report'
    )
    
    # Export historical stats - every 15 minutes
    scheduler.add_job(
        func=export_historical_stats,
        trigger="interval",
        minutes=15,
        id='export_hist_stats'
    )
    
    # Update leaderboard - every 15 minutes
    scheduler.add_job(
        func=update_leaderboard,
        trigger="interval",
        minutes=15,
        id='update_leaderboard'
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
    logger.info("Jobs scheduled:")
    logger.info("- Monthly report: Every 1 hour (test mode)")
    logger.info("- Export historical stats: Every 15 minutes")
    logger.info("- Update leaderboard: Every 15 minutes")
    
    return scheduler