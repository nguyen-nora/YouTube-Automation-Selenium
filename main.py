#!/usr/bin/env python3
"""
YouTube Automation System
A Selenium-based tool for managing multiple Gmail accounts and YouTube video loops.

Features:
- Multi-account Gmail authentication
- Automated YouTube video looping
- View farming capabilities
- Graceful CTRL-C exit support
- Interactive prompts for missing parameters

Usage:
    python main.py [options]

Options:
    --emails <path>     Path to email accounts file (format: email:password per line)
    --video <url>       YouTube video URL to loop
    --headless          Run in headless mode
    --debug             Enable debug logging
    --help              Show this help message
"""

import argparse
import sys
import os
import signal
import threading
from pathlib import Path
from typing import Optional, List, Tuple

# Detect if running as frozen executable
is_frozen = getattr(sys, 'frozen', False)

if is_frozen:
    # When frozen, the src directory is bundled within the executable
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
    sys.path.insert(0, bundle_dir)
else:
    # Add src directory to Python path for development
    sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.youtube_automation import YouTubeAutomation
from account_loader import AccountLoader
from src.logger import logger_config, get_logger
from colorama import Fore, Style, init

init(autoreset=True)

# Get logger instance
logger = get_logger(__name__)


def print_banner():
    """Print the application banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    YouTube Automation System                    ║
║                                                                  ║
║  Multi-Account Gmail + YouTube Loop Automation Tool            ║
║  Built with Selenium WebDriver                                  ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_help():
    """Print detailed help information."""
    help_text = f"""
{Fore.YELLOW}YouTube Automation System - Help{Style.RESET_ALL}

{Fore.CYAN}Description:{Style.RESET_ALL}
This tool automates YouTube video viewing across multiple Gmail accounts using Selenium WebDriver.

{Fore.CYAN}Features:{Style.RESET_ALL}
• Multi-account Gmail authentication
• Automated YouTube video looping
• View farming with human-like behavior simulation
• Configurable browser instances and settings
• Automatic crash recovery and monitoring
• Anti-detection measures

{Fore.CYAN}Configuration:{Style.RESET_ALL}
1. Create an email accounts file with format: email:password per line
2. Have your YouTube video URL ready
3. Run the application with appropriate arguments

{Fore.CYAN}Usage Examples:{Style.RESET_ALL}
  python main.py                                           # Interactive mode - prompts for inputs
  python main.py --emails accounts.txt --video https://youtu.be/VIDEO_ID
  python main.py --emails email.txt --video https://youtube.com/watch?v=VIDEO_ID --headless
  python main.py --emails accounts.txt --video https://youtu.be/VIDEO_ID --debug

{Fore.CYAN}Safety Notes:{Style.RESET_ALL}
• Use responsibly and in accordance with YouTube's Terms of Service
• This tool is for educational and personal use only
• Monitor the automation to ensure it's working as expected
• Be aware of potential IP restrictions or account limitations

{Fore.RED}Disclaimer:{Style.RESET_ALL}
This tool is provided as-is. Users are responsible for compliance with all applicable terms of service and laws.
"""
    print(help_text)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                           # Interactive mode - prompts for inputs
  python main.py --emails accounts.txt --video https://youtu.be/VIDEO_ID
  python main.py --emails email.txt --video https://youtube.com/watch?v=VIDEO_ID --headless
  python main.py --emails accounts.txt --video https://youtu.be/VIDEO_ID --debug

Email file format (one per line):
  user1@gmail.com:password123
  user2@gmail.com:password456
        """
    )
    
    parser.add_argument(
        '--emails',
        type=str,
        help='Path to email accounts file (format: email:password per line)'
    )

    parser.add_argument(
        '--video',
        type=str,
        help='YouTube video URL to loop'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--help-detailed',
        action='store_true',
        help='Show detailed help information'
    )
    
    args = parser.parse_args()
    
    # Show detailed help if requested
    if args.help_detailed:
        print_banner()
        print_help()
        return
    
    # Print banner
    print_banner()
    
    # Prompt for emails file path if not provided
    emails_path = args.emails
    if not emails_path:
        # Check for default email.txt in executable directory if frozen
        if is_frozen:
            default_path = os.path.join(os.path.dirname(sys.executable), 'email.txt')
            if os.path.exists(default_path):
                print(f"{Fore.GREEN}Found email.txt in executable directory")
                emails_path = default_path
            else:
                emails_path = input("Enter path to email accounts file (format: email:password per line): ")
        else:
            emails_path = input("Enter path to email accounts file (format: email:password per line): ")

    # Prompt for video URL if not provided
    video_url = args.video
    if not video_url:
        video_url = input("Enter YouTube video URL to loop: ")

    # Load accounts
    loader = AccountLoader(emails_path)
    try:
        accounts = loader.load_accounts()
        print(f"{Fore.GREEN}Loaded {len(accounts)} accounts from {emails_path}")
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Emails file not found: {emails_path}")
        sys.exit(1)
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}")
        sys.exit(1)

    # Graceful exit support
    stop_event = threading.Event()
    active_threads = []

    def signal_handler(sig, frame):
        print(f"\n{Fore.YELLOW}Received CTRL-C. Stopping all automations gracefully...")
        stop_event.set()
        # Wait for all threads to finish
        for thread in active_threads:
            if thread.is_alive():
                thread.join(timeout=5)
        print(f"{Fore.GREEN}All automations stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Set debug logging if requested
    if args.debug:
        import logging
        logger_config.set_console_level(logging.DEBUG)
        logger.debug("Debug logging enabled")

    print(f"{Fore.CYAN}Starting YouTube Automation System...")
    print(f"{Fore.CYAN}Press Ctrl+C to stop the automation")
    print(f"{Fore.CYAN}" + "="*60)
    print(f"{Fore.YELLOW}Logs are being saved to: {logger_config.get_log_file()}")
    print(f"{Fore.YELLOW}Account status will be saved to: logs/account_status.json")
    print(f"{Fore.CYAN}" + "="*60)

    # Run automation for each account
    def run_account_automation(email: str, password: str, index: int):
        if stop_event.is_set():
            return
        
        logger.info(f"[Account {index + 1}/{len(accounts)}] Starting automation for {email}...")
        automation = YouTubeAutomation()
        
        try:
            # Pass stop_event to support graceful shutdown
            success = automation.run(email, password, video_url, headless=args.headless, stop_event=stop_event, instance_id=index, total_instances=len(accounts))
            
            if success:
                logger_config.log_account_status(
                    email=email,
                    status='SUCCESS',
                    details={
                        'video_url': video_url,
                        'headless': args.headless,
                        'index': index + 1,
                        'total_accounts': len(accounts)
                    }
                )
            else:
                logger_config.log_account_status(
                    email=email,
                    status='FAILED',
                    details={
                        'video_url': video_url,
                        'reason': 'Automation returned false',
                        'index': index + 1,
                        'total_accounts': len(accounts)
                    }
                )
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            logger.error(f"[Account {index + 1}] Error running automation for {email}: {error_type}: {error_msg}")
            
            # Log detailed error information
            logger_config.log_account_status(
                email=email,
                status='ERROR',
                details={
                    'video_url': video_url,
                    'error_type': error_type,
                    'error_message': error_msg,
                    'index': index + 1,
                    'total_accounts': len(accounts)
                }
            )
            
        finally:
            logger.info(f"[Account {index + 1}] Automation stopped for {email}")

    # Create threads for each account
    for i, (email, password) in enumerate(accounts):
        if stop_event.is_set():
            break
            
        thread = threading.Thread(
            target=run_account_automation,
            args=(email, password, i),
            daemon=True
        )
        active_threads.append(thread)
        thread.start()
        
        # Small delay between starting accounts
        if i < len(accounts) - 1:
            threading.Event().wait(2)

    # Wait for all threads to complete or stop signal
    try:
        for thread in active_threads:
            thread.join()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

    if not stop_event.is_set():
        print(f"{Fore.GREEN}All automations completed successfully.")
    else:
        print(f"{Fore.YELLOW}Automation was interrupted.")


if __name__ == "__main__":
    main()
