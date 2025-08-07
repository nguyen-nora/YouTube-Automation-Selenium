import time
import threading
import signal
import sys
from typing import Dict, Any, List
from selenium import webdriver
from colorama import Fore, Style, init

from .config_manager import ConfigManager
from .browser_manager_enhanced import BrowserManagerEnhanced
from .gmail_authenticator_enhanced import GmailAuthenticatorEnhanced
from .youtube_automation import YouTubeAutomation

init(autoreset=True)


class MainController:
    """Main controller for the YouTube automation system."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.browser_manager = BrowserManagerEnhanced(self.config_manager.config)
        self.gmail_authenticator = GmailAuthenticatorEnhanced(self.browser_manager, self.config_manager.config)
        self.youtube_automation = YouTubeAutomation(self.browser_manager, self.config_manager.config)
        
        self.running_instances = {}
        self.stop_flag = False
        self.monitoring_thread = None
        
        # Get max concurrent instances from config
        automation_settings = self.config_manager.get_automation_settings()
        max_concurrent = automation_settings.get('max_concurrent_instances', 5)
        
        # Create semaphore for throttling concurrent instances
        self.instance_semaphore = threading.Semaphore(max_concurrent)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n{Fore.YELLOW}[Main Controller] Received shutdown signal. Stopping all processes...")
        self.stop_all_processes()
        sys.exit(0)
    
    def start_automation(self):
        """Start the main automation process."""
        try:
            print(f"{Fore.CYAN}[Main Controller] Starting YouTube Automation System")
            print(f"{Fore.CYAN}[Main Controller] Loading configuration and accounts...")
            
            # Get enabled accounts
            accounts = self.config_manager.get_enabled_accounts()
            if not accounts:
                print(f"{Fore.RED}[Main Controller] No enabled accounts found. Please configure accounts.json")
                return False
            
            print(f"{Fore.GREEN}[Main Controller] Found {len(accounts)} enabled accounts")
            
            # Get YouTube settings
            youtube_settings = self.config_manager.get_youtube_settings()
            video_urls = youtube_settings.get('video_urls', [])
            if not video_urls:
                print(f"{Fore.RED}[Main Controller] No YouTube URLs configured. Please update config.json")
                return False
            
            print(f"{Fore.GREEN}[Main Controller] Configured {len(video_urls)} YouTube URLs")
            
            # Get automation settings
            automation_settings = self.config_manager.get_automation_settings()
            max_instances = automation_settings.get('max_concurrent_instances', 5)
            startup_delay = automation_settings.get('instance_startup_delay', 10)
            
            total_instances = min(len(accounts), max_instances)
            
            # Start instances for each account
            for i, account in enumerate(accounts):
                if self.stop_flag:
                    break
                
                account_name = account.get('nickname', account.get('email'))
                
                # Log current state
                active_count = len([t for t in self.running_instances.values() if t.is_alive()])
                print(f"{Fore.CYAN}[Main Controller] Instance {i+1}/{len(accounts)} - Active: {active_count}/{max_instances}")
                
                # Wait for available slot using semaphore
                if active_count >= max_instances:
                    print(f"{Fore.YELLOW}[Main Controller] Max instances reached. Waiting for slot (account: {account_name})...")
                else:
                    print(f"{Fore.CYAN}[Main Controller] Slot available for {account_name}")
                
                acquired_time = time.time()
                self.instance_semaphore.acquire()
                wait_time = time.time() - acquired_time
                
                if wait_time > 0.1:  # Only log if we actually waited
                    print(f"{Fore.GREEN}[Main Controller] Acquired slot after {wait_time:.1f}s wait")
                
                if self.stop_flag:
                    self.instance_semaphore.release()
                    break
                
                # Start instance in separate thread
                instance_thread = threading.Thread(
                    target=self._run_account_instance_with_semaphore,
                    args=(account, video_urls, i, total_instances),
                    daemon=True
                )
                
                self.running_instances[account_name] = instance_thread
                instance_thread.start()
                
                print(f"{Fore.GREEN}[Main Controller] Started instance for {account_name} (Thread ID: {instance_thread.ident})")
                
                # Delay between instance startups to avoid simultaneous Chrome spawning
                if i < len(accounts) - 1:  # Don't delay after the last instance
                    print(f"{Fore.CYAN}[Main Controller] Staggering startup: waiting {startup_delay}s before next instance...")
                    time.sleep(startup_delay)
            
            # Start monitoring thread
            self.start_monitoring()
            
            # Keep main thread alive
            while not self.stop_flag:
                time.sleep(10)
                
                # Check if all instances are still running
                active_instances = [name for name, thread in self.running_instances.items() if thread.is_alive()]
                if not active_instances:
                    print(f"{Fore.YELLOW}[Main Controller] All instances have stopped")
                    break
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[Main Controller] Error in automation: {e}")
            return False
        finally:
            self.stop_all_processes()
    
    def _run_account_instance_with_semaphore(self, account: Dict[str, Any], video_urls: List[str], instance_id: int, total_instances: int):
        """Wrapper method that ensures semaphore is released after instance completes."""
        account_name = account.get('nickname', account.get('email'))
        start_time = time.time()
        
        try:
            print(f"{Fore.CYAN}[Main Controller] Thread started for {account_name}")
            self._run_account_instance(account, video_urls, instance_id, total_instances)
        finally:
            # Always release the semaphore when instance completes
            self.instance_semaphore.release()
            elapsed = time.time() - start_time
            print(f"{Fore.CYAN}[Main Controller] Released instance slot for {account_name} after {elapsed:.1f}s")
    
    def _run_account_instance(self, account: Dict[str, Any], video_urls: List[str], instance_id: int, total_instances: int):
        """Run automation for a single account."""
        driver = None
        account_nickname = account.get('nickname', account.get('email'))
        
        try:
            print(f"{Fore.CYAN}[Instance {instance_id}] Starting for {account_nickname}")
            
            # Create browser instance with email for profile
            email = account.get('email')
            driver = self.browser_manager.create_driver(instance_id, total_instances, email)
            if not driver:
                print(f"{Fore.RED}[Instance {instance_id}] Failed to create browser instance")
                return
            
            # Login to Gmail
            if not self.gmail_authenticator.login_to_gmail(driver, account):
                print(f"{Fore.RED}[Instance {instance_id}] Failed to login to Gmail")
                return
            
            # Start YouTube loops
            for video_url in video_urls:
                if self.stop_flag:
                    break
                
                if self.youtube_automation.start_youtube_loop(driver, video_url, account_nickname):
                    print(f"{Fore.GREEN}[Instance {instance_id}] Started YouTube loop for {video_url}")
                else:
                    print(f"{Fore.RED}[Instance {instance_id}] Failed to start YouTube loop for {video_url}")
                
                # Small delay between starting multiple videos
                time.sleep(2)
            
            # Keep instance running while loops are active
            while not self.stop_flag and self.youtube_automation.is_loop_running(account_nickname):
                time.sleep(30)  # Check every 30 seconds
                
                # Refresh driver if needed
                driver = self.browser_manager.refresh_driver(driver)
            
            print(f"{Fore.YELLOW}[Instance {instance_id}] Completed for {account_nickname}")
            
        except Exception as e:
            print(f"{Fore.RED}[Instance {instance_id}] Error for {account_nickname}: {e}")
        finally:
            # Cleanup
            if driver:
                self.browser_manager.close_driver(driver)
            
            # Remove from running instances
            if account_nickname in self.running_instances:
                del self.running_instances[account_nickname]
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        print(f"{Fore.GREEN}[Main Controller] Monitoring started")
    
    def _monitoring_worker(self):
        """Monitoring worker thread."""
        monitoring_interval = self.config_manager.get_automation_settings().get('monitoring_interval', 30)
        
        while not self.stop_flag:
            try:
                # Display status
                active_instances = len([thread for thread in self.running_instances.values() if thread.is_alive()])
                active_loops = self.youtube_automation.get_running_loops_count()
                
                print(f"{Fore.BLUE}[Monitoring] Active instances: {active_instances}, Active loops: {active_loops}")
                
                # Check for crashed instances and restart if enabled
                if self.config_manager.get_automation_settings().get('auto_restart_on_crash', True):
                    self._check_and_restart_crashed_instances()
                
                time.sleep(monitoring_interval)
                
            except Exception as e:
                print(f"{Fore.RED}[Monitoring] Error: {e}")
                time.sleep(monitoring_interval)
    
    def _check_and_restart_crashed_instances(self):
        """Check for crashed instances and restart them."""
        try:
            accounts = self.config_manager.get_enabled_accounts()
            
            for account in accounts:
                account_nickname = account.get('nickname', account.get('email'))
                
                # Check if instance is supposed to be running but isn't
                if account_nickname in self.running_instances:
                    thread = self.running_instances[account_nickname]
                    if not thread.is_alive() and not self.stop_flag:
                        print(f"{Fore.YELLOW}[Monitoring] Restarting crashed instance for {account_nickname}")
                        
                        # Remove old thread
                        del self.running_instances[account_nickname]
                        
                        # Acquire semaphore for restart
                        if self.instance_semaphore.acquire(blocking=False):
                            # Start new instance
                            instance_thread = threading.Thread(
                                target=self._run_account_instance_with_semaphore,
                                args=(account, self.config_manager.get_youtube_settings().get('video_urls', []), 0, 0), # Pass 0 for total_instances as it's a restart
                                daemon=True
                            )
                            
                            self.running_instances[account_nickname] = instance_thread
                            instance_thread.start()
                        else:
                            print(f"{Fore.YELLOW}[Monitoring] Cannot restart {account_nickname} - max instances reached")
                        
        except Exception as e:
            print(f"{Fore.RED}[Monitoring] Error checking crashed instances: {e}")
    
    def stop_all_processes(self):
        """Stop all running processes."""
        print(f"{Fore.YELLOW}[Main Controller] Stopping all processes...")
        
        self.stop_flag = True
        
        # Stop all YouTube loops
        self.youtube_automation.stop_all_loops()
        
        # Close all browser instances
        self.browser_manager.close_all_drivers()
        
        # Wait for threads to finish
        for name, thread in self.running_instances.items():
            if thread.is_alive():
                thread.join(timeout=10)
        
        print(f"{Fore.GREEN}[Main Controller] All processes stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'active_instances': len([thread for thread in self.running_instances.values() if thread.is_alive()]),
            'active_loops': self.youtube_automation.get_running_loops_count(),
            'total_accounts': len(self.config_manager.get_enabled_accounts()),
            'running_loops': list(self.youtube_automation.running_loops.keys()),
            'stop_flag': self.stop_flag
        }
    
    def pause_automation(self):
        """Pause all automation."""
        print(f"{Fore.YELLOW}[Main Controller] Pausing automation...")
        self.youtube_automation.stop_all_loops()
    
    def resume_automation(self):
        """Resume automation."""
        print(f"{Fore.GREEN}[Main Controller] Resuming automation...")
        # This would need to be implemented to restart loops
        # For now, it's a placeholder
        pass 