import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from colorama import Fore, Style, init
import json

init(autoreset=True)

class GoogleSelectorDiagnostic:
    """Diagnostic tool to check Google login selectors and identify UI changes."""
    
    def __init__(self):
        self.results = {
            "tested_selectors": {},
            "found_elements": {},
            "alternative_selectors": {},
            "page_structure": {}
        }
        
        # Current selectors being used
        self.current_selectors = {
            'email_input': 'input[type="email"]',
            'password_input': 'input[type="password"]',
            'next_button': '#identifierNext button',
            'password_next_button': '#passwordNext button',
            'signin_button': 'button[type="submit"]',
            'account_picker': 'div[data-email]',
            'use_another_account': 'div[data-email=""]',
            'add_account': 'div[data-email=""]'
        }
        
        # Alternative selectors to test
        self.alternative_selectors = {
            'email_input': [
                'input[type="email"]',
                'input[name="identifier"]',
                'input[id="identifierId"]',
                'input[autocomplete="username"]',
                'input[aria-label*="Email"]',
                'input[aria-label*="Phone"]'
            ],
            'password_input': [
                'input[type="password"]',
                'input[name="password"]',
                'input[name="Passwd"]',
                'input[autocomplete="current-password"]',
                'input[aria-label*="password"]'
            ],
            'next_button': [
                '#identifierNext button',
                '#identifierNext',
                'button:has-text("Next")',
                'div[id="identifierNext"]',
                'button[jsname="LgbsSe"]',
                'div[role="button"][id="identifierNext"]'
            ],
            'password_next_button': [
                '#passwordNext button',
                '#passwordNext',
                'button:has-text("Next")',
                'div[id="passwordNext"]',
                'button[jsname="LgbsSe"]',
                'div[role="button"][id="passwordNext"]'
            ]
        }
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options."""
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def test_selector(self, driver, selector_name, selector):
        """Test a single selector and return results."""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                element_info = []
                for i, elem in enumerate(elements[:3]):  # Check first 3 matches
                    info = {
                        "index": i,
                        "visible": elem.is_displayed(),
                        "enabled": elem.is_enabled(),
                        "tag": elem.tag_name,
                        "text": elem.text[:50] if elem.text else "",
                        "id": elem.get_attribute("id"),
                        "name": elem.get_attribute("name"),
                        "class": elem.get_attribute("class"),
                        "aria-label": elem.get_attribute("aria-label")
                    }
                    element_info.append(info)
                return True, element_info
            return False, None
        except Exception as e:
            return False, str(e)
    
    def analyze_page_structure(self, driver):
        """Analyze the current page structure to find form elements."""
        try:
            # Get all input fields
            inputs = driver.find_elements(By.TAG_NAME, "input")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            divs_with_role_button = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
            
            page_info = {
                "url": driver.current_url,
                "title": driver.title,
                "inputs": [],
                "buttons": [],
                "clickable_divs": []
            }
            
            # Analyze inputs
            for inp in inputs[:10]:  # Limit to first 10
                if inp.is_displayed():
                    page_info["inputs"].append({
                        "type": inp.get_attribute("type"),
                        "name": inp.get_attribute("name"),
                        "id": inp.get_attribute("id"),
                        "placeholder": inp.get_attribute("placeholder"),
                        "aria-label": inp.get_attribute("aria-label"),
                        "autocomplete": inp.get_attribute("autocomplete")
                    })
            
            # Analyze buttons
            for btn in buttons[:10]:
                if btn.is_displayed():
                    page_info["buttons"].append({
                        "text": btn.text[:30],
                        "id": btn.get_attribute("id"),
                        "class": btn.get_attribute("class"),
                        "type": btn.get_attribute("type"),
                        "jsname": btn.get_attribute("jsname")
                    })
            
            # Analyze clickable divs
            for div in divs_with_role_button[:10]:
                if div.is_displayed():
                    page_info["clickable_divs"].append({
                        "text": div.text[:30],
                        "id": div.get_attribute("id"),
                        "class": div.get_attribute("class")
                    })
            
            return page_info
        except Exception as e:
            return {"error": str(e)}
    
    def run_diagnostics(self):
        """Run comprehensive diagnostics on Google login page."""
        driver = None
        try:
            print(f"{Fore.CYAN}=== Google Login Selector Diagnostics ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Setting up Chrome driver...{Style.RESET_ALL}")
            
            driver = self.setup_driver()
            
            # Navigate to Google login
            print(f"{Fore.YELLOW}Navigating to Google login page...{Style.RESET_ALL}")
            driver.get("https://accounts.google.com/signin")
            time.sleep(3)  # Wait for page load
            
            # Analyze page structure
            print(f"\n{Fore.CYAN}Analyzing page structure...{Style.RESET_ALL}")
            self.results["page_structure"]["login_page"] = self.analyze_page_structure(driver)
            
            # Test current selectors
            print(f"\n{Fore.CYAN}Testing current selectors...{Style.RESET_ALL}")
            for name, selector in self.current_selectors.items():
                found, info = self.test_selector(driver, name, selector)
                self.results["tested_selectors"][name] = {
                    "selector": selector,
                    "found": found,
                    "info": info
                }
                if found:
                    print(f"{Fore.GREEN}✓ {name}: Found{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ {name}: Not found{Style.RESET_ALL}")
            
            # Test alternative selectors
            print(f"\n{Fore.CYAN}Testing alternative selectors...{Style.RESET_ALL}")
            for element_type, selectors in self.alternative_selectors.items():
                print(f"\n{Fore.YELLOW}Testing {element_type} alternatives:{Style.RESET_ALL}")
                working_alternatives = []
                
                for selector in selectors:
                    found, info = self.test_selector(driver, element_type, selector)
                    if found:
                        working_alternatives.append({
                            "selector": selector,
                            "info": info
                        })
                        print(f"{Fore.GREEN}  ✓ {selector}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}  ✗ {selector}{Style.RESET_ALL}")
                
                self.results["alternative_selectors"][element_type] = working_alternatives
            
            # Try to interact with email field
            print(f"\n{Fore.CYAN}Testing email field interaction...{Style.RESET_ALL}")
            email_field = None
            for selector in self.alternative_selectors['email_input']:
                try:
                    email_field = driver.find_element(By.CSS_SELECTOR, selector)
                    if email_field and email_field.is_displayed():
                        email_field.click()
                        email_field.send_keys("test@example.com")
                        print(f"{Fore.GREEN}✓ Successfully interacted with email field using: {selector}{Style.RESET_ALL}")
                        self.results["found_elements"]["working_email_selector"] = selector
                        break
                except:
                    continue
            
            # Check if next button becomes enabled
            time.sleep(1)
            print(f"\n{Fore.CYAN}Checking Next button state...{Style.RESET_ALL}")
            for selector in self.alternative_selectors['next_button']:
                try:
                    next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if next_btn and next_btn.is_displayed():
                        print(f"{Fore.GREEN}✓ Next button found and visible: {selector}{Style.RESET_ALL}")
                        print(f"  Enabled: {next_btn.is_enabled()}")
                        self.results["found_elements"]["working_next_button_selector"] = selector
                        
                        # Try clicking (but don't proceed with actual login)
                        if next_btn.is_enabled():
                            print(f"{Fore.YELLOW}  Next button is clickable{Style.RESET_ALL}")
                        break
                except:
                    continue
            
            # Generate recommendations
            print(f"\n{Fore.CYAN}=== Recommendations ==={Style.RESET_ALL}")
            self.generate_recommendations()
            
            # Save results
            with open('google_selector_diagnostic_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n{Fore.GREEN}Results saved to google_selector_diagnostic_results.json{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error during diagnostics: {e}{Style.RESET_ALL}")
        finally:
            if driver:
                driver.quit()
    
    def generate_recommendations(self):
        """Generate recommendations based on diagnostic results."""
        recommendations = []
        
        # Check email input
        if not self.results["tested_selectors"].get("email_input", {}).get("found"):
            if self.results["alternative_selectors"].get("email_input"):
                working = self.results["alternative_selectors"]["email_input"][0]["selector"]
                recommendations.append(f"Update email_input selector to: '{working}'")
        
        # Check next button
        if not self.results["tested_selectors"].get("next_button", {}).get("found"):
            if self.results["alternative_selectors"].get("next_button"):
                working = self.results["alternative_selectors"]["next_button"][0]["selector"]
                recommendations.append(f"Update next_button selector to: '{working}'")
        
        # Print recommendations
        if recommendations:
            print(f"{Fore.YELLOW}Recommended selector updates:{Style.RESET_ALL}")
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print(f"{Fore.GREEN}All current selectors appear to be working correctly.{Style.RESET_ALL}")
        
        self.results["recommendations"] = recommendations

if __name__ == "__main__":
    diagnostic = GoogleSelectorDiagnostic()
    diagnostic.run_diagnostics()
