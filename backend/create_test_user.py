"""
Create Test User for SmartGriev Login
Run this script to create a test user account.

Usage:
    cd E:\\Smartgriv\\smartgriev\\backend
    python create_test_user.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user():
    """Create a test user for login testing"""
    
    print("=" * 60)
    print("SmartGriev - Test User Creation")
    print("=" * 60)
    
    # Test user credentials
    username = 'testuser'
    email = 'test@example.com'
    password = 'Test@123'
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"\n⚠️  User '{username}' already exists!")
            
            user = User.objects.get(username=username)
            print(f"\n📊 Existing User Details:")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Active: {'✅ Yes' if user.is_active else '❌ No'}")
            print(f"   Staff: {'✅ Yes' if user.is_staff else '❌ No'}")
            print(f"   Superuser: {'✅ Yes' if user.is_superuser else '❌ No'}")
            
            # Ask to update
            update = input("\n Do you want to update this user? (y/n): ")
            if update.lower() == 'y':
                user.email = email
                user.set_password(password)
                user.is_active = True
                user.save()
                print(f"\n✅ User '{username}' updated successfully!")
            else:
                print("\n ℹ️  User not updated.")
                
        else:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Test',
                last_name='User',
                is_active=True
            )
            print(f"\n✅ User created successfully!")
        
        print(f"\n📝 Login Credentials:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        
        print(f"\n🔐 User Status:")
        print(f"   Active: {'✅ Yes' if user.is_active else '❌ No'}")
        print(f"   Can Login: ✅ Yes")
        
        print(f"\n🌐 Test Login:")
        print(f"   1. Go to: http://localhost:3001/login")
        print(f"   2. Enter username: {username}")
        print(f"   3. Enter password: {password}")
        print(f"   4. Click 'Sign In'")
        
        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def list_all_users():
    """List all existing users"""
    print("\n" + "=" * 60)
    print("All Users in Database")
    print("=" * 60)
    
    users = User.objects.all()
    
    if not users:
        print("\n⚠️  No users found in database!")
        return
    
    for i, user in enumerate(users, 1):
        print(f"\n{i}. {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Active: {'✅' if user.is_active else '❌'}")
        print(f"   Staff: {'✅' if user.is_staff else '❌'}")
        print(f"   Superuser: {'✅' if user.is_superuser else '❌'}")
        print(f"   Last Login: {user.last_login or 'Never'}")

def create_superuser():
    """Create a superuser for Django admin"""
    print("\n" + "=" * 60)
    print("Create Superuser for Django Admin")
    print("=" * 60)
    
    username = 'admin'
    email = 'admin@smartgriev.com'
    password = 'admin123'
    
    try:
        if User.objects.filter(username=username).exists():
            print(f"\n⚠️  Superuser '{username}' already exists!")
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print(f"\n✅ Superuser created successfully!")
        print(f"\n📝 Admin Credentials:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n🌐 Django Admin:")
        print(f"   URL: http://127.0.0.1:8000/admin")
        
    except Exception as e:
        print(f"\n❌ Error creating superuser: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartGriev User Management')
    parser.add_argument('--list', action='store_true', help='List all users')
    parser.add_argument('--superuser', action='store_true', help='Create superuser')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_users()
    elif args.superuser:
        create_superuser()
    else:
        create_test_user()
    
    print("\n")
