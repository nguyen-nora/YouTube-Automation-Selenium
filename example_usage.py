"""
Example usage of the AccountLoader class.
"""
from account_loader import AccountLoader


def main():
    """Demonstrate how to use AccountLoader."""
    
    # Example 1: Basic usage with default filename
    print("Example 1: Basic usage")
    print("-" * 40)
    
    # Create a sample email.txt file
    sample_accounts = """john.doe@example.com:password123
jane.smith@company.org:secure_pass456
admin@website.net:admin_password
support@service.io:support2024
"""
    
    with open("email.txt", "w") as f:
        f.write(sample_accounts)
    
    # Load accounts using default file
    loader = AccountLoader()
    accounts = loader.load_accounts()
    
    print(f"Loaded {len(accounts)} accounts from email.txt:")
    for i, (email, password) in enumerate(accounts, 1):
        print(f"  {i}. Email: {email}")
        print(f"     Password: {password}")
    
    # Example 2: Using a custom filename
    print("\n\nExample 2: Custom filename")
    print("-" * 40)
    
    # Create accounts in a different file
    with open("credentials.txt", "w") as f:
        f.write("user1@test.com:pass1\nuser2@test.com:pass2")
    
    custom_loader = AccountLoader("credentials.txt")
    custom_accounts = custom_loader.load_accounts()
    
    print(f"Loaded {len(custom_accounts)} accounts from credentials.txt:")
    for email, password in custom_accounts:
        print(f"  - {email} / {password}")
    
    # Example 3: Using generator for memory efficiency
    print("\n\nExample 3: Using generator (memory efficient)")
    print("-" * 40)
    
    # For large files, use generator to save memory
    loader = AccountLoader()
    print("Processing accounts one by one:")
    
    for i, (email, password) in enumerate(loader.load_accounts_generator(), 1):
        print(f"  Processing account {i}: {email}")
        # Here you could process each account individually
        # e.g., login, perform actions, etc.
    
    # Example 4: Error handling
    print("\n\nExample 4: Error handling")
    print("-" * 40)
    
    # Try to load non-existent file
    try:
        error_loader = AccountLoader("missing_file.txt")
        error_loader.load_accounts()
    except FileNotFoundError as e:
        print(f"  Error handled: {e}")
    
    # Create file with invalid email
    with open("invalid_emails.txt", "w") as f:
        f.write("valid@email.com:password\ninvalid-email:password")
    
    try:
        invalid_loader = AccountLoader("invalid_emails.txt")
        invalid_loader.load_accounts()
    except ValueError as e:
        print(f"  Error handled: {e}")
    
    # Example 5: Using get_accounts method
    print("\n\nExample 5: Using get_accounts method")
    print("-" * 40)
    
    loader = AccountLoader()
    
    # Get as list
    accounts_list = loader.get_accounts(as_generator=False)
    print(f"Got {len(accounts_list)} accounts as list")
    
    # Get as generator
    accounts_gen = loader.get_accounts(as_generator=True)
    print("Got accounts as generator")
    print(f"First account: {next(accounts_gen)}")
    
    # Clean up
    import os
    for file in ["email.txt", "credentials.txt", "invalid_emails.txt"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n\nDemo completed!")


if __name__ == "__main__":
    main()
