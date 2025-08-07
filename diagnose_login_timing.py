#!/usr/bin/env python3
"""
Diagnose Login Timing Issues
This script tests login behavior and timing to identify if logins are being cut short
"""

import time
import json
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

init(autoreset=True)

class LoginTimingDiagnostic:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'login_stages': [],
            'timing_info': {},
            'blocking_indicators': {},
            'recommendations': []
        }
        
    def test_login_flow(self, email=None, password=None):
        """Test the complete login flow with detailed timing information."""
        driver = None
        
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Login Timing Diagnostic")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Get test credentials if not provided
        if not email or not password:
            print(f"{Fore.YELLOW}Using test login (will stop before password entry)")
            email = "test@example.com"
            password = "dummy"
            test_mode = True
        else:
            test_mode = False
        
        try:
            # Setup Chrome
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Try to use local Chrome
            chrome_path = r"E:\SeleniumYtb\chrome-win64\chrome.exe"
            if Path(chrome_path).exists():
                options.binary_location = chrome_path
            
            print(f"{Fore.YELLOW}Starting Chrome driver...")
            driver = webdriver.Chrome(options=options)
            
            # Stage 1: Navigate to Gmail
            stage_start = time.time()
            print(f"\n{Fore.CYAN}Stage 1: Navigating to Gmail...")
            driver.get("https://gmail.com")
            
            # Wait for page load
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            navigation_time = time.time() - stage_start
            self.results['login_stages'].append({
                'stage': 'navigation',
                'time': round(navigation_time, 2),
                'success': True
            })
            print(f"{Fore.GREEN}✓ Navigation completed in {navigation_time:.2f}s")
            
            # Check current URL
            current_url = driver.current_url
            print(f"{Fore.CYAN}Current URL: {current_url}")
            
            # Stage 2: Check for existing login
            stage_start = time.time()
            print(f"\n{Fore.CYAN}Stage 2: Checking for existing login...")
            
            # Check if already logged in
            is_logged_in = False
            if "mail.google.com" in current_url:
                # Check for Gmail interface elements
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]'))
                    )
                    is_logged_in = True
                    print(f"{Fore.GREEN}✓ Already logged in!")
                except:
                    pass
            
            check_time = time.time() - stage_start
            self.results['login_stages'].append({
                'stage': 'check_existing_login',
                'time': round(check_time, 2),
                'already_logged_in': is_logged_in
            })
            
            if is_logged_in:
                print(f"{Fore.YELLOW}Already logged in - clearing session for test...")
                driver.get("https://accounts.google.com/Logout")
                time.sleep(3)
                driver.get("https://gmail.com")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
                )
            
            # Stage 3: Email Entry
            stage_start = time.time()
            print(f"\n{Fore.CYAN}Stage 3: Email entry stage...")
            
            # Wait for email field
            try:
                email_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
                )
                
                # Check page for blocking indicators
                page_source = driver.page_source.lower()
                self.check_blocking_indicators(page_source, "email_stage")
                
                # Enter email
                email_field.clear()
                time.sleep(0.5)
                email_field.send_keys(email)
                time.sleep(1)
                
                # Find and click next button
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#identifierNext button'))
                )
                
                if test_mode:
                    print(f"{Fore.YELLOW}Test mode - stopping before clicking Next")
                else:
                    next_button.click()
                    
                email_time = time.time() - stage_start
                self.results['login_stages'].append({
                    'stage': 'email_entry',
                    'time': round(email_time, 2),
                    'success': True
                })
                print(f"{Fore.GREEN}✓ Email entry completed in {email_time:.2f}s")
                
            except TimeoutException:
                email_time = time.time() - stage_start
                self.results['login_stages'].append({
                    'stage': 'email_entry',
                    'time': round(email_time, 2),
                    'success': False,
                    'error': 'Timeout waiting for email field'
                })
                print(f"{Fore.RED}✗ Email entry failed - timeout after {email_time:.2f}s")
                return
            
            if not test_mode:
                # Stage 4: Wait for password page
                stage_start = time.time()
                print(f"\n{Fore.CYAN}Stage 4: Waiting for password page...")
                
                try:
                    # Wait for password field to appear
                    password_field = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                    )
                    
                    # Check URL change
                    new_url = driver.current_url
                    print(f"{Fore.CYAN}New URL: {new_url}")
                    
                    # Check for challenges or blocks
                    page_source = driver.page_source.lower()
                    self.check_blocking_indicators(page_source, "password_stage")
                    
                    # Check for 2FA or other challenges
                    if self.check_for_challenges(driver):
                        print(f"{Fore.YELLOW}⚠ Additional challenges detected!")
                    
                    password_wait_time = time.time() - stage_start
                    self.results['login_stages'].append({
                        'stage': 'password_page_load',
                        'time': round(password_wait_time, 2),
                        'success': True
                    })
                    print(f"{Fore.GREEN}✓ Password page loaded in {password_wait_time:.2f}s")
                    
                    # Enter password
                    stage_start = time.time()
                    print(f"\n{Fore.CYAN}Stage 5: Password entry...")
                    
                    password_field.clear()
                    time.sleep(0.5)
                    
                    # Type password slowly
                    for char in password:
                        password_field.send_keys(char)
                        time.sleep(0.1)
                    
                    time.sleep(1)
                    
                    # Find and click next button
                    password_next = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '#passwordNext button'))
                    )
                    password_next.click()
                    
                    password_time = time.time() - stage_start
                    self.results['login_stages'].append({
                        'stage': 'password_entry',
                        'time': round(password_time, 2),
                        'success': True
                    })
                    print(f"{Fore.GREEN}✓ Password entry completed in {password_time:.2f}s")
                    
                    # Stage 6: Wait for login completion
                    stage_start = time.time()
                    print(f"\n{Fore.CYAN}Stage 6: Waiting for login completion...")
                    
                    try:
                        # Wait for redirect to Gmail
                        WebDriverWait(driver, 30).until(
                            lambda d: "mail.google.com" in d.current_url or "gmail.com" in d.current_url
                        )
                        
                        # Verify Gmail interface loaded
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]'))
                        )
                        
                        completion_time = time.time() - stage_start
                        self.results['login_stages'].append({
                            'stage': 'login_completion',
                            'time': round(completion_time, 2),
                            'success': True
                        })
                        print(f"{Fore.GREEN}✓ Login completed successfully in {completion_time:.2f}s")
                        
                    except TimeoutException:
                        completion_time = time.time() - stage_start
                        
                        # Check what page we're on
                        current_url = driver.current_url
                        page_source = driver.page_source.lower()
                        
                        self.results['login_stages'].append({
                            'stage': 'login_completion',
                            'time': round(completion_time, 2),
                            'success': False,
                            'current_url': current_url,
                            'error': 'Timeout waiting for Gmail'
                        })
                        
                        print(f"{Fore.RED}✗ Login did not complete after {completion_time:.2f}s")
                        print(f"{Fore.YELLOW}Still on: {current_url}")
                        
                        # Check for specific issues
                        self.check_blocking_indicators(page_source, "completion_stage")
                        
                except TimeoutException:
                    password_wait_time = time.time() - stage_start
                    self.results['login_stages'].append({
                        'stage': 'password_page_load',
                        'time': round(password_wait_time, 2),
                        'success': False,
                        'error': 'Timeout waiting for password field'
                    })
                    print(f"{Fore.RED}✗ Password page did not load after {password_wait_time:.2f}s")
            
            # Calculate total time
            total_time = sum(stage['time'] for stage in self.results['login_stages'])
            self.results['timing_info']['total_time'] = round(total_time, 2)
            
            # Generate analysis
            self.analyze_results()
            
        except Exception as e:
            print(f"{Fore.RED}Error during diagnostic: {e}")
            self.results['error'] = str(e)
            
        finally:
            if driver:
                input(f"\n{Fore.YELLOW}Press Enter to close the browser...")
                driver.quit()
            
            # Save results
            self.save_results()
    
    def check_blocking_indicators(self, page_source, stage):
        """Check for various blocking indicators in the page."""
        indicators = {
            'captcha': 'captcha' in page_source or 'recaptcha' in page_source,
            'unusual_activity': 'unusual' in page_source and 'activity' in page_source,
            'verify_identity': 'verify' in page_source and 'identity' in page_source,
            'suspicious': 'suspicious' in page_source,
            'automated': 'automated' in page_source,
            'too_many_requests': 'too many' in page_source and 'requests' in page_source,
            'rate_limit': 'rate' in page_source and 'limit' in page_source,
            'blocked': 'blocked' in page_source,
            'denied': 'denied' in page_source,
            'forbidden': 'forbidden' in page_source
        }
        
        detected = {k: v for k, v in indicators.items() if v}
        
        if detected:
            self.results['blocking_indicators'][stage] = detected
            print(f"{Fore.YELLOW}⚠ Blocking indicators detected at {stage}:")
            for indicator in detected:
                print(f"  - {indicator}")
    
    def check_for_challenges(self, driver):
        """Check for additional challenges like 2FA, phone verification, etc."""
        challenges = []
        
        # Check URL for challenge patterns
        current_url = driver.current_url
        challenge_patterns = [
            'challenge/totp', 'challenge/ipp', 'challenge/az',
            'challenge/sk', 'signin/v2/challenge'
        ]
        
        for pattern in challenge_patterns:
            if pattern in current_url:
                challenges.append(f"URL contains {pattern}")
        
        # Check for specific elements
        challenge_selectors = [
            ('2FA', 'input[name="totpPin"]'),
            ('Phone verification', 'input[type="tel"]'),
            ('Security question', 'input[name="answer"]'),
            ('Recovery email', 'input[name="knowledgePreregisteredEmailResponse"]')
        ]
        
        for name, selector in challenge_selectors:
            try:
                driver.find_element(By.CSS_SELECTOR, selector)
                challenges.append(name)
            except:
                pass
        
        if challenges:
            self.results['challenges_detected'] = challenges
        
        return len(challenges) > 0
    
    def analyze_results(self):
        """Analyze the results and generate recommendations."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Analysis Results")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Total timing analysis
        total_time = self.results['timing_info'].get('total_time', 0)
        print(f"\n{Fore.YELLOW}Total login time: {total_time}s")
        
        # Stage timing analysis
        print(f"\n{Fore.YELLOW}Stage breakdown:")
        for stage in self.results['login_stages']:
            status = "✓" if stage.get('success', False) else "✗"
            color = Fore.GREEN if stage.get('success', False) else Fore.RED
            print(f"{color}{status} {stage['stage']}: {stage['time']}s")
            if 'error' in stage:
                print(f"  {Fore.RED}Error: {stage['error']}")
        
        # Blocking indicators
        if self.results['blocking_indicators']:
            print(f"\n{Fore.YELLOW}Blocking indicators found:")
            for stage, indicators in self.results['blocking_indicators'].items():
                print(f"  {stage}: {', '.join(indicators.keys())}")
        
        # Generate recommendations
        recommendations = []
        
        # Check for slow stages
        slow_stages = [s for s in self.results['login_stages'] if s['time'] > 5.0]
        if slow_stages:
            recommendations.append({
                'issue': 'Slow login stages detected',
                'detail': f"Stages taking >5s: {', '.join(s['stage'] for s in slow_stages)}",
                'solution': 'Network may be slow or Google servers may be throttling. Try: 1) Different network, 2) VPN, 3) Reduce concurrent logins'
            })
        
        # Check for failures
        failed_stages = [s for s in self.results['login_stages'] if not s.get('success', True)]
        if failed_stages:
            recommendations.append({
                'issue': 'Login stages failed',
                'detail': f"Failed stages: {', '.join(s['stage'] for s in failed_stages)}",
                'solution': 'Increase timeout values in gmail_settings in config.json'
            })
        
        # Check for blocking
        if self.results['blocking_indicators']:
            if any('captcha' in indicators for indicators in self.results['blocking_indicators'].values()):
                recommendations.append({
                    'issue': 'CAPTCHA detected',
                    'detail': 'Google is showing CAPTCHA challenges',
                    'solution': 'IP may be flagged. Try: 1) Different IP/network, 2) Residential proxy, 3) Manual login first'
                })
            
            if any('rate' in str(indicators) or 'too many' in str(indicators) 
                   for indicators in self.results['blocking_indicators'].values()):
                recommendations.append({
                    'issue': 'Rate limiting detected',
                    'detail': 'Google is rate-limiting login attempts',
                    'solution': 'Reduce max_concurrent_instances to 2-3 and increase instance_startup_delay to 30-60 seconds'
                })
        
        # Check total time
        if total_time > 30:
            recommendations.append({
                'issue': 'Login process too slow',
                'detail': f'Total login time: {total_time}s (should be <30s)',
                'solution': 'Network or rate-limiting issues. Try from different network or reduce load'
            })
        
        self.results['recommendations'] = recommendations
        
        # Print recommendations
        if recommendations:
            print(f"\n{Fore.CYAN}Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{Fore.YELLOW}{i}. {rec['issue']}")
                print(f"   {Fore.WHITE}Detail: {rec['detail']}")
                print(f"   {Fore.GREEN}Solution: {rec['solution']}")
        else:
            print(f"\n{Fore.GREEN}No major issues detected!")
    
    def save_results(self):
        """Save results to JSON file."""
        filename = f"login_timing_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{Fore.GREEN}Results saved to {filename}")


def main():
    """Run the login timing diagnostic."""
    diagnostic = LoginTimingDiagnostic()
    
    print(f"{Fore.YELLOW}This diagnostic will test the Gmail login process timing.")
    print(f"{Fore.YELLOW}You can either:")
    print(f"  1. Run a test with dummy credentials (stops before password)")
    print(f"  2. Provide real credentials for full test")
    
    choice = input(f"\n{Fore.CYAN}Use real credentials? (y/n): ").lower()
    
    if choice == 'y':
        email = input(f"{Fore.CYAN}Enter email: ")
        password = input(f"{Fore.CYAN}Enter password: ")
        diagnostic.test_login_flow(email, password)
    else:
        diagnostic.test_login_flow()


if __name__ == "__main__":
    main()
