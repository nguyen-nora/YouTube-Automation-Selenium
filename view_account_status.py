#!/usr/bin/env python3
"""
View Account Status Utility
Reads and displays the account status from the logs/account_status.json file.
"""

import json
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init
import argparse

init(autoreset=True)


def view_account_status(status_file: Path = Path("logs/account_status.json")):
    """Read and display account status from the JSON log file."""
    
    if not status_file.exists():
        print(f"{Fore.YELLOW}No account status file found at: {status_file}")
        return
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error reading status file: Invalid JSON")
        return
    except Exception as e:
        print(f"{Fore.RED}Error reading status file: {e}")
        return
    
    if not status_data:
        print(f"{Fore.YELLOW}No account status entries found")
        return
    
    # Group by email
    account_history = {}
    for entry in status_data:
        email = entry.get('email', 'Unknown')
        if email not in account_history:
            account_history[email] = []
        account_history[email].append(entry)
    
    # Display summary
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Account Status Summary")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    total_accounts = len(account_history)
    success_count = 0
    failed_count = 0
    error_count = 0
    
    for email, history in account_history.items():
        # Get latest status
        latest_entry = history[-1]
        status = latest_entry.get('status', 'UNKNOWN')
        
        if status == 'SUCCESS':
            success_count += 1
            status_color = Fore.GREEN
        elif status == 'FAILED':
            failed_count += 1
            status_color = Fore.YELLOW
        elif status == 'ERROR':
            error_count += 1
            status_color = Fore.RED
        else:
            status_color = Fore.WHITE
        
        print(f"{Fore.BLUE}Account: {email}")
        print(f"  Latest Status: {status_color}{status}{Style.RESET_ALL}")
        
        # Parse timestamp
        timestamp_str = latest_entry.get('timestamp', '')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                print(f"  Last Updated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"  Last Updated: {timestamp_str}")
        
        # Show details
        details = latest_entry.get('details', {})
        if details:
            if 'video_url' in details:
                print(f"  Video URL: {details['video_url']}")
            if 'error_type' in details:
                print(f"  Error Type: {Fore.RED}{details['error_type']}{Style.RESET_ALL}")
            if 'error_message' in details:
                print(f"  Error Message: {Fore.RED}{details['error_message']}{Style.RESET_ALL}")
            if 'reason' in details:
                print(f"  Reason: {Fore.YELLOW}{details['reason']}{Style.RESET_ALL}")
        
        # Show attempt history
        if len(history) > 1:
            print(f"  Total Attempts: {len(history)}")
        
        print()
    
    # Summary statistics
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Summary Statistics")
    print(f"{Fore.CYAN}{'='*80}")
    print(f"Total Accounts: {total_accounts}")
    print(f"{Fore.GREEN}Successful: {success_count} ({success_count/total_accounts*100:.1f}%)")
    print(f"{Fore.YELLOW}Failed: {failed_count} ({failed_count/total_accounts*100:.1f}%)")
    print(f"{Fore.RED}Errors: {error_count} ({error_count/total_accounts*100:.1f}%)")
    print()


def view_detailed_history(status_file: Path = Path("logs/account_status.json"), email: str = None):
    """View detailed history for a specific account or all accounts."""
    
    if not status_file.exists():
        print(f"{Fore.YELLOW}No account status file found at: {status_file}")
        return
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error reading status file: {e}")
        return
    
    # Filter by email if specified
    if email:
        status_data = [entry for entry in status_data if entry.get('email') == email]
        if not status_data:
            print(f"{Fore.YELLOW}No entries found for email: {email}")
            return
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Detailed Account History")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    for entry in status_data:
        email = entry.get('email', 'Unknown')
        status = entry.get('status', 'UNKNOWN')
        timestamp_str = entry.get('timestamp', '')
        details = entry.get('details', {})
        
        # Status color
        if status == 'SUCCESS':
            status_color = Fore.GREEN
        elif status == 'FAILED':
            status_color = Fore.YELLOW
        elif status == 'ERROR':
            status_color = Fore.RED
        else:
            status_color = Fore.WHITE
        
        print(f"{Fore.BLUE}[{timestamp_str}] {email}")
        print(f"  Status: {status_color}{status}{Style.RESET_ALL}")
        
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
        
        print()


def main():
    parser = argparse.ArgumentParser(description="View account status from automation logs")
    parser.add_argument(
        '--file',
        type=str,
        default="logs/account_status.json",
        help='Path to account status JSON file'
    )
    parser.add_argument(
        '--email',
        type=str,
        help='Filter by specific email address'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed history for all attempts'
    )
    
    args = parser.parse_args()
    
    status_file = Path(args.file)
    
    if args.detailed:
        view_detailed_history(status_file, args.email)
    else:
        view_account_status(status_file)


if __name__ == "__main__":
    main()
