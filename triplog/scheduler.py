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

def run_stats_and_leaderboard():
    """Function to run export historical stats first, then update leaderboard"""
    try:
        logger.info("Starting combined stats and leaderboard update job...")
        
        # First: Export historical stats
        logger.info("Step 1: Running export historical stats...")
        call_command('export_hist_stats')
        logger.info("Export historical stats completed successfully")
        
        # Second: Update leaderboard (which may depend on the exported stats)
        logger.info("Step 2: Running update leaderboard...")
        call_command('update_leaderboard')
        logger.info("Update leaderboard completed successfully")
        
        logger.info("Combined stats and leaderboard update job completed successfully")
    except Exception as e:
        logger.error(f"Combined stats and leaderboard update job failed: {e}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Test job - every 2 minutes
    # scheduler.add_job(
    #     func=run_monthly_report,
    #     trigger="interval",
    #     # minutes=2,
    #     hours=1,
    #     id='test_monthly_report'
    # )
    
    # Combined job - export historical stats then update leaderboard - every 15 minutes
    scheduler.add_job(
        func=run_stats_and_leaderboard,
        trigger="interval",
        minutes=15,
        id='stats_and_leaderboard'
    )
    
    # Production job - 25th of every month at 9 AM
    scheduler.add_job(
        func=run_monthly_report,
        trigger="cron",
        day=25,
        hour=9,
        minute=0,
        id='monthly_report'
    )
    
    scheduler.start()
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info("Scheduler started successfully")
    logger.info("Jobs scheduled:")
    logger.info("- Monthly report: 25th of every month at 9 AM")
    logger.info("- Combined stats export and leaderboard update: Every 15 minutes")
    
    return scheduler