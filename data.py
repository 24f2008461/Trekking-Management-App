import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db, USER, TREKK, BOOKING

first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Sam", "Jamie", "Chris", "Pat", "Drew", "Cameron", "Jesse", "Avery", "Dakota", "Peyton", "Skyler", "Reese", "Rowan", "Hayden", "Quinn", "Parker", "Emerson", "Finley", "Blake"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]

trek_names = ["Everest Base Camp", "Annapurna Circuit", "Inca Trail", "Kilimanjaro", "Tour du Mont Blanc", "Patagonia W Trek", "Zion Narrows", "Grand Canyon Rim", "Yosemite Half Dome", "Kalalau Trail", "Laugavegur Trail", "Routeburn Track", "West Highland Way"]
locations = ["Nepal", "Peru", "Tanzania", "France", "Chile", "USA", "Iceland", "New Zealand", "Scotland"]
difficulties = ["Easy", "Moderate", "Hard"]
statuses = ["Pending", "Approved", "Open", "Closed", "Completed"]

def generate_phone():
    return f"+1{random.randint(1000000000, 9999999999)}"

with app.app_context():
    print("Clearing old data (keeping admin)...")
    db.session.query(BOOKING).delete()
    db.session.query(TREKK).delete()
    db.session.query(USER).filter(USER.role != "admin").delete()
    db.session.commit()

    print("Generating 10 Staff members...")
    staff_list = []
    for i in range(10):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        u = USER(
            username=f"staff_{fname.lower()}_{i+1}",
            email=f"staff{i+1}@trekking.com",
            password=generate_password_hash("password123"),
            fullname=f"{fname} {lname} (Staff)",
            phone_number=generate_phone(),
            role="staff"
        )
        db.session.add(u)
        staff_list.append(u)
    db.session.commit()

    print("Generating 10 Treks...")
    trek_list = []
    for i in range(10):
        t_name = random.choice(trek_names)
        slots = random.randint(15, 50)
        start_dt = datetime.utcnow() + timedelta(days=random.randint(-10, 60))
        end_dt = start_dt + timedelta(days=random.randint(2, 14))
        
        status = random.choice(statuses)
        if start_dt < datetime.utcnow() and status not in ["Completed", "Closed", "Open"]:
            status = "Pending"
            
        t = TREKK(
            name=f"{t_name} Expedition {i+1}",
            difficulty=random.choice(difficulties),
            location=random.choice(locations),
            duration=(end_dt - start_dt).days,
            total_slots=slots,
            avl_slots=slots,
            assigned_staff_id=random.choice(staff_list).user_id,
            description=f"Experience the ultimate adventure at {t_name} with breathtaking views and unforgettable trails.",
            price=round(random.uniform(100, 2000), 2),
            status=status,
            start_date=start_dt.date(),
            end_date=end_dt.date()
        )
        db.session.add(t)
        trek_list.append(t)
    db.session.commit()

    print("Generating 50 Users (Trekkers)...")
    user_list = []
    for i in range(50):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        u = USER(
            username=f"trekker_{fname.lower()}_{i+1}",
            email=f"user{i+1}@trekking.com",
            password=generate_password_hash("password123"),
            fullname=f"{fname} {lname}",
            phone_number=generate_phone(),
            role="user"
        )
        db.session.add(u)
        user_list.append(u)
    db.session.commit()

    
    db.session.commit()
    print("Database seeded successfully! (Passwords are 'password123')")