"""
Account loader module for reading and validating email credentials from a file.
"""
from typing import List, Tuple, Generator, Union
import os


class AccountLoader:
    """
    A class to load and validate email account credentials from a text file.
    
    The expected file format is one account per line: email:password
    """
    
    def __init__(self, filepath: str = "email.txt"):
        """
        Initialize the AccountLoader with a file path.
        
        Args:
            filepath (str): Path to the file containing email credentials.
                           Defaults to "email.txt" in the current directory.
        """
        self.filepath = filepath
    
    def _validate_email(self, email: str) -> bool:
        """
        Validate if an email address contains the @ symbol.
        
        Args:
            email (str): The email address to validate.
            
        Returns:
            bool: True if email contains @, False otherwise.
        """
        return "@" in email
    
    def load_accounts(self) -> List[Tuple[str, str]]:
        """
        Load all accounts from the file and return them as a list.
        
        Returns:
            List[Tuple[str, str]]: A list of (email, password) tuples.
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist.
            ValueError: If a line doesn't have the correct format or email is invalid.
        """
        accounts = []
        
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # Strip whitespace from the line
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split by colon
                parts = line.split(':', 1)
                
                if len(parts) != 2:
                    raise ValueError(f"Invalid format on line {line_num}: {line}")
                
                email, password = parts
                
                # Strip whitespace from email and password
                email = email.strip()
                password = password.strip()
                
                # Validate email
                if not self._validate_email(email):
                    raise ValueError(f"Invalid email on line {line_num}: {email} (missing @ symbol)")
                
                accounts.append((email, password))
        
        return accounts
    
    def load_accounts_generator(self) -> Generator[Tuple[str, str], None, None]:
        """
        Load accounts from the file as a generator (memory efficient for large files).
        
        Yields:
            Tuple[str, str]: (email, password) tuples one at a time.
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist.
            ValueError: If a line doesn't have the correct format or email is invalid.
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                # Strip whitespace from the line
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split by colon
                parts = line.split(':', 1)
                
                if len(parts) != 2:
                    raise ValueError(f"Invalid format on line {line_num}: {line}")
                
                email, password = parts
                
                # Strip whitespace from email and password
                email = email.strip()
                password = password.strip()
                
                # Validate email
                if not self._validate_email(email):
                    raise ValueError(f"Invalid email on line {line_num}: {email} (missing @ symbol)")
                
                yield (email, password)
    
    def get_accounts(self, as_generator: bool = False) -> Union[List[Tuple[str, str]], Generator[Tuple[str, str], None, None]]:
        """
        Get accounts either as a list or generator based on preference.
        
        Args:
            as_generator (bool): If True, returns a generator; otherwise returns a list.
            
        Returns:
            Union[List[Tuple[str, str]], Generator[Tuple[str, str], None, None]]: 
                Account tuples as list or generator.
        """
        if as_generator:
            return self.load_accounts_generator()
        else:
            return self.load_accounts()


# Example usage
if __name__ == "__main__":
    # Create a sample email.txt file for testing
    sample_content = """user1@example.com:password123
    user2@domain.com  :  pass456  
    admin@site.org:adminpass
    
    test@test.com:testpass
    """
    
    # Write sample file
    with open("email.txt", "w") as f:
        f.write(sample_content)
    
    # Test the loader
    loader = AccountLoader("email.txt")
    
    print("Loading accounts as list:")
    try:
        accounts = loader.load_accounts()
        for email, password in accounts:
            print(f"  Email: {email}, Password: {password}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nLoading accounts as generator:")
    try:
        for email, password in loader.load_accounts_generator():
            print(f"  Email: {email}, Password: {password}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Clean up test file
    os.remove("email.txt")
