from authentication.models import User
from complaints.models import Complaint

print("\n=== RECENT USERS ===")
users = User.objects.all().order_by('-date_joined')[:10]
for u in users:
    print(f"Username: {u.username}, Email: {u.email}, Name: {u.first_name} {u.last_name}")

print("\n=== RECENT COMPLAINTS ===")
complaints = Complaint.objects.all().order_by('-created_at')[:10]
for c in complaints:
    print(f"ID: {c.id}, User: {c.user.username}, Title: {c.title}, Status: {c.status}")

print("\n=== LOOKING FOR KANCHA ===")
kancha_users = User.objects.filter(email__icontains='kancha')
for u in kancha_users:
    print(f"Found: Username={u.username}, Email={u.email}")
    user_complaints = Complaint.objects.filter(user=u)
    print(f"  Complaints: {user_complaints.count()}")
    for c in user_complaints:
        print(f"    - #{c.id}: {c.title}")
