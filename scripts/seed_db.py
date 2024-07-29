import os
from decimal import Decimal
from app import create_app, db
from app.db import User, SavingsGoal

# Create the Flask application
app = create_app()

# Set up the application context
with app.app_context():
    # Check if the user already exists
    existing_user = User.query.filter_by(email="manya@example.com").first()
    if existing_user is None:
        # Create a new user
        new_user = User(
            name="Manya",
            email="manya@example.com",
            password="password",
            session_id="session_id",
            monthly_pocket_money="500.00",
            monthly_expenses=[{"category": "food", "amount": 50}, {"category": "transport", "amount": 30}],
            savings_goal="1000.00"
        )

        db.session.add(new_user)
        db.session.commit()

    # Create a savings goal for the user
        goal = SavingsGoal(
            name="Vacation",
            target_amount="1500.00",
            current_amount="200.00",
            user_id=new_user.id
        )

        db.session.add(goal)
        db.session.commit()
    else:
        print("User with email 'manya@example.com' already exists.")