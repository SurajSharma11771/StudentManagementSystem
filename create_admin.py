from app.database_sqlite import init_db, add_user

# Database aur tables create karo (agar pehle se nahi bane)
init_db()

# Pehla admin user create karo
add_user("admin", "admin123")

print("Admin user created successfully!")
print("Username: admin")
print("Password: admin123")