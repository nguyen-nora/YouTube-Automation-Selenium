import json
import os
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)


class EnhancedMonitor:
    """Monitor and display statistics for the enhanced automation system."""
    
    def __init__(self):
        self.rate_limit_file = 'logs/rate_limit_tracker.json'
        self.failed_accounts_file = 'logs/failed_accounts.json'
        self.account_status_file = 'logs/account_status.json'
    
    def load_json_file(self, filepath):
        """Load JSON file safely."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error loading {filepath}: {e}")
        return {}
    
    def display_dashboard(self):
        """Display comprehensive dashboard."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{'Enhanced YouTube Automation Monitor':^80}")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        # Load data
        rate_limits = self.load_json_file(self.rate_limit_file)
        failed_accounts = self.load_json_file(self.failed_accounts_file)
        account_status = self.load_json_file(self.account_status_file)
        
        # Display statistics
        self.display_rate_limit_status(rate_limits)
        self.display_failed_accounts(failed_accounts)
        self.display_recent_activity(account_status)
        self.display_recommendations(rate_limits, failed_accounts)
    
    def display_rate_limit_status(self, rate_limits):
        """Display rate limit status for all accounts."""
        print(f"{Fore.YELLOW}\n📊 Rate Limit Status:")
        print(f"{Fore.YELLOW}{'-'*60}")
        
        if not rate_limits:
            print(f"{Fore.GREEN}No rate limit data available yet.")
            return
        
        current_time = datetime.now()
        active_cooldowns = 0
        
        for email, data in rate_limits.items():
            attempts_hour = len([a for a in data['attempts'] 
                               if datetime.fromisoformat(a) > current_time - timedelta(hours=1)])
            
            status = f"{Fore.GREEN}Active"
            if data['last_cooldown']:
                cooldown_end = datetime.fromisoformat(data['last_cooldown']) + timedelta(minutes=5)
                if current_time < cooldown_end:
                    remaining = int((cooldown_end - current_time).total_seconds() / 60)
                    status = f"{Fore.RED}Cooldown ({remaining}m remaining)"
                    active_cooldowns += 1
            
            print(f"  {email}: {attempts_hour}/10 attempts | Status: {status}")
        
        print(f"\n  {Fore.CYAN}Total accounts in cooldown: {active_cooldowns}")
    
    def display_failed_accounts(self, failed_accounts):
        """Display failed accounts and reasons."""
        print(f"{Fore.YELLOW}\n❌ Failed Accounts:")
        print(f"{Fore.YELLOW}{'-'*60}")
        
        if not failed_accounts:
            print(f"{Fore.GREEN}No failed accounts!")
            return
        
        captcha_count = 0
        tfa_count = 0
        other_count = 0
        
        for email, data in failed_accounts.items():
            reasons = data.get('reasons', [])
            failure_count = data.get('failures', 0)
            
            # Count failure types
            if any('CAPTCHA' in r for r in reasons):
                captcha_count += 1
                reason = "CAPTCHA"
                color = Fore.MAGENTA
            elif any('2FA' in r or '2fa' in r for r in reasons):
                tfa_count += 1
                reason = "2FA"
                color = Fore.YELLOW
            else:
                other_count += 1
                reason = "Other"
                color = Fore.RED
            
            last_failure = data.get('last_failure', 'Unknown')
            if last_failure != 'Unknown':
                try:
                    last_failure_dt = datetime.fromisoformat(last_failure)
                    last_failure = last_failure_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            print(f"  {color}{email}: {failure_count} failures | Reason: {reason} | Last: {last_failure}")
        
        print(f"\n  {Fore.CYAN}Summary: CAPTCHA: {captcha_count}, 2FA: {tfa_count}, Other: {other_count}")
    
    def display_recent_activity(self, account_status):
        """Display recent account activity."""
        print(f"{Fore.YELLOW}\n📝 Recent Activity (Last 10):")
        print(f"{Fore.YELLOW}{'-'*60}")
        
        if not account_status:
            print(f"{Fore.GREEN}No activity recorded yet.")
            return
        
        # Sort by timestamp
        recent_activities = sorted(account_status[-10:], 
                                 key=lambda x: x.get('timestamp', ''), 
                                 reverse=True)
        
        for activity in recent_activities:
            timestamp = activity.get('timestamp', 'Unknown')
            email = activity.get('email', 'Unknown')
            status = activity.get('status', 'Unknown')
            details = activity.get('details', {})
            
            color = Fore.GREEN if status == 'SUCCESS' else Fore.RED
            
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp_str = dt.strftime("%H:%M:%S")
            except:
                timestamp_str = timestamp
            
            print(f"  {timestamp_str} | {color}{email} | {status}")
            
            if status == 'FAILED' and 'reason' in details:
                print(f"           └─ {Fore.YELLOW}Reason: {details['reason']}")
    
    def display_recommendations(self, rate_limits, failed_accounts):
        """Display recommendations based on current status."""
        print(f"{Fore.YELLOW}\n💡 Recommendations:")
        print(f"{Fore.YELLOW}{'-'*60}")
        
        recommendations = []
        
        # Check for high failure rate
        if len(failed_accounts) > len(rate_limits) * 0.5:
            recommendations.append(
                f"{Fore.RED}High failure rate detected! Consider:\n"
                f"  - Increasing delays between logins\n"
                f"  - Using residential proxies\n"
                f"  - Checking if accounts are compromised"
            )
        
        # Check for CAPTCHA issues
        captcha_accounts = sum(1 for data in failed_accounts.values() 
                              if any('CAPTCHA' in r for r in data.get('reasons', [])))
        if captcha_accounts > 2:
            recommendations.append(
                f"{Fore.MAGENTA}Multiple CAPTCHA blocks detected! Consider:\n"
                f"  - Reducing concurrent instances\n"
                f"  - Increasing stagger delays\n"
                f"  - Switching IP addresses\n"
                f"  - Using anti-captcha services"
            )
        
        # Check for 2FA issues
        tfa_accounts = sum(1 for data in failed_accounts.values() 
                          if any('2FA' in r or '2fa' in r for r in data.get('reasons', [])))
        if tfa_accounts > 0:
            recommendations.append(
                f"{Fore.YELLOW}{tfa_accounts} accounts have 2FA enabled:\n"
                f"  - Disable 2FA for automation accounts\n"
                f"  - Use app passwords if available\n"
                f"  - Consider manual intervention"
            )
        
        # Check for rate limiting
        current_time = datetime.now()
        rate_limited = sum(1 for data in rate_limits.values()
                          if data.get('last_cooldown') and 
                          datetime.fromisoformat(data['last_cooldown']) + timedelta(minutes=5) > current_time)
        if rate_limited > 0:
            recommendations.append(
                f"{Fore.ORANGE}{rate_limited} accounts are rate limited:\n"
                f"  - Wait for cooldown periods\n"
                f"  - Reduce login frequency\n"
                f"  - Stagger login attempts more"
            )
        
        if not recommendations:
            print(f"{Fore.GREEN}✓ System is operating normally!")
        else:
            for rec in recommendations:
                print(f"\n{rec}")
    
    def continuous_monitor(self, refresh_interval=5):
        """Run continuous monitoring with auto-refresh."""
        print(f"{Fore.CYAN}Starting continuous monitoring (refresh every {refresh_interval}s)")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop...")
        time.sleep(2)
        
        try:
            while True:
                self.display_dashboard()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped.")


def main():
    """Main entry point."""
    monitor = EnhancedMonitor()
    
    print(f"{Fore.CYAN}Enhanced YouTube Automation Monitor")
    print(f"{Fore.YELLOW}1. Show current status")
    print(f"{Fore.YELLOW}2. Continuous monitoring")
    print(f"{Fore.YELLOW}3. Export statistics")
    
    choice = input(f"\n{Fore.GREEN}Select option (1-3): ")
    
    if choice == '1':
        monitor.display_dashboard()
    elif choice == '2':
        interval = input(f"{Fore.GREEN}Refresh interval in seconds (default 5): ").strip()
        interval = int(interval) if interval.isdigit() else 5
        monitor.continuous_monitor(interval)
    elif choice == '3':
        # Export statistics
        stats = {
            'timestamp': datetime.now().isoformat(),
            'rate_limits': monitor.load_json_file(monitor.rate_limit_file),
            'failed_accounts': monitor.load_json_file(monitor.failed_accounts_file),
            'recent_activity': monitor.load_json_file(monitor.account_status_file)[-50:]
        }
        
        filename = f"stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"{Fore.GREEN}Statistics exported to {filename}")
    else:
        print(f"{Fore.RED}Invalid option")


if __name__ == "__main__":
    main()
