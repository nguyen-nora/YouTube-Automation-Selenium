import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from colorama import Fore, Style, init

init(autoreset=True)

class PasswordPageDiagnostic:
    """Advanced diagnostic tool to test password page selectors."""
    
    def __init__(self):
        self.results = {
            "password_page_selectors": {},
            "password_page_structure": {},
            "interaction_test": {},
            "selector_recommendations": []
        }
        
        # Password page selectors to test
        self.password_selectors = {
            'password_input': [
                'input[type="password"]',
                'input[name="password"]', 
                'input[name="Passwd"]',
                'input[autocomplete="current-password"]',
                'input[aria-label*="password"]',
                'input[jsname="YPqjbf"]',
                'input#password',
                'div[jsname="YRMmle"] input'
            ],
            'password_next_button': [
                '#passwordNext button',
                '#passwordNext',
                'button:contains("Next")',
                'div[id="passwordNext"]',
                'button[jsname="LgbsSe"]',
                'div[role="button"][id="passwordNext"]',
                'div#passwordNext button[jsname="LgbsSe"]'
            ],
            'show_password_toggle': [
                'div[jsname="RCGCUb"]',
                'div[aria-label*="Show password"]',
                'div[role="button"][aria-label*="password"]'
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
    
    def navigate_to_password_page(self, driver, test_email="test.account@gmail.com"):
        """Navigate through email entry to reach password page."""
        try:
            # Navigate to login page
            driver.get("https://accounts.google.com/signin")
            time.sleep(2)
            
            # Find and fill email field
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
            )
            email_field.clear()
            email_field.send_keys(test_email)
            time.sleep(1)
            
            # Click Next
            next_button = driver.find_element(By.CSS_SELECTOR, '#identifierNext button')
            next_button.click()
            
            # Wait for password page to load
            time.sleep(3)
            
            # Check if we reached password page or got an error
            current_url = driver.current_url
            if "challenge/pwd" in current_url or "signin/v2/challenge" in current_url:
                return True
            elif "signin/v2/identifier" in current_url:
                # Still on identifier page - might be invalid email
                print(f"{Fore.YELLOW}Still on identifier page - email might be invalid{Style.RESET_ALL}")
                return True  # Continue anyway to test selectors
            else:
                print(f"{Fore.YELLOW}Unexpected URL: {current_url}{Style.RESET_ALL}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"{Fore.RED}Error navigating to password page: {e}{Style.RESET_ALL}")
            return False
    
    def test_selector_with_wait(self, driver, selector, timeout=5):
        """Test a selector with explicit wait."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Get detailed element information
            info = {
                "found": True,
                "visible": element.is_displayed(),
                "enabled": element.is_enabled(),
                "tag": element.tag_name,
                "id": element.get_attribute("id"),
                "name": element.get_attribute("name"),
                "type": element.get_attribute("type"),
                "class": element.get_attribute("class"),
                "aria-label": element.get_attribute("aria-label"),
                "jsname": element.get_attribute("jsname"),
                "autocomplete": element.get_attribute("autocomplete")
            }
            
            # Try to get parent structure
            try:
                parent = element.find_element(By.XPATH, "..")
                info["parent_tag"] = parent.tag_name
                info["parent_class"] = parent.get_attribute("class")
            except:
                pass
                
            return True, info
            
        except TimeoutException:
            return False, None
        except Exception as e:
            return False, str(e)
    
    def analyze_password_page_structure(self, driver):
        """Analyze the password page structure in detail."""
        try:
            structure = {
                "url": driver.current_url,
                "title": driver.title,
                "all_inputs": [],
                "all_buttons": [],
                "password_related_elements": []
            }
            
            # Find all inputs
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                try:
                    if inp.get_attribute("type") in ["password", "text", "email"]:
                        structure["all_inputs"].append({
                            "type": inp.get_attribute("type"),
                            "name": inp.get_attribute("name"),
                            "id": inp.get_attribute("id"),
                            "visible": inp.is_displayed(),
                            "jsname": inp.get_attribute("jsname"),
                            "aria-label": inp.get_attribute("aria-label")
                        })
                except:
                    pass
            
            # Find all buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                try:
                    structure["all_buttons"].append({
                        "text": btn.text,
                        "id": btn.get_attribute("id"),
                        "visible": btn.is_displayed(),
                        "jsname": btn.get_attribute("jsname"),
                        "parent_id": btn.find_element(By.XPATH, "..").get_attribute("id") if btn.find_element(By.XPATH, "..") else None
                    })
                except:
                    pass
            
            # Find elements with password-related text
            password_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'password') or contains(text(), 'Password')]")
            for elem in password_elements[:5]:
                try:
                    structure["password_related_elements"].append({
                        "tag": elem.tag_name,
                        "text": elem.text[:50],
                        "class": elem.get_attribute("class")
                    })
                except:
                    pass
            
            return structure
            
        except Exception as e:
            return {"error": str(e)}
    
    def test_password_interaction(self, driver):
        """Test interaction with password field."""
        results = {
            "field_found": False,
            "field_clickable": False,
            "field_accepts_input": False,
            "working_selector": None
        }
        
        for selector in self.password_selectors['password_input']:
            try:
                # Try to find the element
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        results["field_found"] = True
                        results["working_selector"] = selector
                        
                        # Try to click
                        try:
                            element.click()
                            results["field_clickable"] = True
                            
                            # Try to type
                            element.send_keys("test123")
                            time.sleep(0.5)
                            
                            # Check if input was accepted
                            value = element.get_attribute("value")
                            if value:
                                results["field_accepts_input"] = True
                                # Clear the field
                                element.clear()
                            
                            return results
                            
                        except Exception as e:
                            print(f"{Fore.YELLOW}Interaction failed for {selector}: {e}{Style.RESET_ALL}")
                            
            except:
                continue
                
        return results
    
    def run_diagnostics(self):
        """Run comprehensive password page diagnostics."""
        driver = None
        try:
            print(f"{Fore.CYAN}=== Password Page Selector Diagnostics ==={Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Setting up Chrome driver...{Style.RESET_ALL}")
            
            driver = self.setup_driver()
            
            # Navigate to password page
            print(f"{Fore.YELLOW}Navigating to password page...{Style.RESET_ALL}")
            if not self.navigate_to_password_page(driver):
                print(f"{Fore.RED}Failed to navigate to password page{Style.RESET_ALL}")
                return
            
            # Analyze page structure
            print(f"\n{Fore.CYAN}Analyzing password page structure...{Style.RESET_ALL}")
            self.results["password_page_structure"] = self.analyze_password_page_structure(driver)
            
            # Test password input selectors
            print(f"\n{Fore.CYAN}Testing password input selectors...{Style.RESET_ALL}")
            for selector in self.password_selectors['password_input']:
                found, info = self.test_selector_with_wait(driver, selector, timeout=2)
                if found:
                    print(f"{Fore.GREEN}✓ {selector}{Style.RESET_ALL}")
                    if info.get('visible'):
                        print(f"  Visible: Yes, Name: {info.get('name')}, ID: {info.get('id')}")
                else:
                    print(f"{Fore.RED}✗ {selector}{Style.RESET_ALL}")
                
                self.results["password_page_selectors"][selector] = {
                    "found": found,
                    "info": info
                }
            
            # Test password next button selectors
            print(f"\n{Fore.CYAN}Testing password next button selectors...{Style.RESET_ALL}")
            for selector in self.password_selectors['password_next_button']:
                found, info = self.test_selector_with_wait(driver, selector, timeout=2)
                if found:
                    print(f"{Fore.GREEN}✓ {selector}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ {selector}{Style.RESET_ALL}")
                
                self.results["password_page_selectors"][f"next_{selector}"] = {
                    "found": found,
                    "info": info
                }
            
            # Test password field interaction
            print(f"\n{Fore.CYAN}Testing password field interaction...{Style.RESET_ALL}")
            interaction_results = self.test_password_interaction(driver)
            self.results["interaction_test"] = interaction_results
            
            if interaction_results["field_accepts_input"]:
                print(f"{Fore.GREEN}✓ Successfully interacted with password field{Style.RESET_ALL}")
                print(f"  Working selector: {interaction_results['working_selector']}")
            else:
                print(f"{Fore.RED}✗ Failed to interact with password field{Style.RESET_ALL}")
            
            # Generate recommendations
            self.generate_recommendations()
            
            # Save results
            with open('password_selector_diagnostic_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n{Fore.GREEN}Results saved to password_selector_diagnostic_results.json{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error during diagnostics: {e}{Style.RESET_ALL}")
        finally:
            if driver:
                driver.quit()
    
    def generate_recommendations(self):
        """Generate selector recommendations based on findings."""
        print(f"\n{Fore.CYAN}=== Recommendations ==={Style.RESET_ALL}")
        
        # Find working password input selector
        working_password_selector = None
        for selector, data in self.results["password_page_selectors"].items():
            if data["found"] and data.get("info", {}).get("visible") and "password" in selector:
                working_password_selector = selector
                break
        
        if working_password_selector:
            self.results["selector_recommendations"].append({
                "element": "password_input",
                "recommended_selector": working_password_selector,
                "reason": "Visible and accessible password field"
            })
            print(f"{Fore.YELLOW}• Recommended password input selector: {working_password_selector}{Style.RESET_ALL}")
        
        # Find working next button selector
        working_next_selector = None
        for selector, data in self.results["password_page_selectors"].items():
            if selector.startswith("next_") and data["found"] and data.get("info", {}).get("visible"):
                working_next_selector = selector.replace("next_", "")
                break
        
        if working_next_selector:
            self.results["selector_recommendations"].append({
                "element": "password_next_button",
                "recommended_selector": working_next_selector,
                "reason": "Visible and accessible next button"
            })
            print(f"{Fore.YELLOW}• Recommended password next button selector: {working_next_selector}{Style.RESET_ALL}")

if __name__ == "__main__":
    diagnostic = PasswordPageDiagnostic()
    diagnostic.run_diagnostics()
