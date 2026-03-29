#!/usr/bin/env python
"""
Initialize production environment with default data
This script runs during Docker container startup
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elite_wealth_capital.settings')
django.setup()

from django.contrib.auth import get_user_model
from dashboard.models import SiteSettings


def main():
    """Initialize production environment"""
    print("=" * 60)
    print("🚀 INITIALIZING PRODUCTION ENVIRONMENT")
    print("=" * 60)
    
    # 1. Create or get SiteSettings
    print("\n📊 Step 1: Initializing Site Settings...")
    try:
        settings = SiteSettings.get_settings()
        print(f"✅ Site Settings initialized (ID: {settings.id})")
        print(f"   Company: {settings.company_name}")
        print(f"   Email: {settings.company_email}")
    except Exception as e:
        print(f"❌ Error creating site settings: {e}")
        return False
    
    # 2. Create admin user if doesn't exist (uses environment variables)
    print("\n👤 Step 2: Creating Admin User...")
    User = get_user_model()
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@elitewealthcapita.uk')
    admin_password = os.environ.get('ADMIN_PASSWORD', '')
    
    try:
        if User.objects.filter(email=admin_email).exists():
            print(f"ℹ️  Admin user already exists: {admin_email}")
            admin = User.objects.get(email=admin_email)
            # Ensure admin has correct permissions
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_active = True
            admin.save()
            print("✅ Admin permissions verified")
        elif admin_password:
            admin = User.objects.create_superuser(
                email=admin_email,
                password=admin_password
            )
            print(f"✅ Admin user created: {admin_email}")
        else:
            print("⚠️  ADMIN_PASSWORD not set - skipping admin creation")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    
    # 3. Verify database connection
    print("\n🔗 Step 3: Verifying Database Connection...")
    try:
        user_count = User.objects.count()
        print(f"✅ Database connected successfully")
        print(f"   Total users in database: {user_count}")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    # Success
    print("\n" + "=" * 60)
    print("🎉 PRODUCTION INITIALIZATION COMPLETE!")
    print("=" * 60)
    print("\n📋 Summary:")
    print(f"   ✅ Site Settings: Ready")
    print(f"   ✅ Admin User: {admin_email}")
    print(f"   ✅ Database: Connected ({user_count} users)")
    print("\n🔐 Admin Login:")
    print(f"   URL: https://elitewealthcapita.uk/admin/")
    print(f"   Email: {admin_email}")
    print("=" * 60)
    print()
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
