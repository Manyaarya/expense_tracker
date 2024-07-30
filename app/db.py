from flask_sqlalchemy import SQLAlchemy
import datetime
from decimal import Decimal
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.Text, nullable=False)

    # New fields
    monthly_pocket_money = db.Column(db.String(20), nullable=True)  # Store as string
    monthly_expenses = db.Column(db.JSON, nullable=True)  # Stores a list of expenses
    savings_goal = db.Column(db.String(20), nullable=True)  # Store as string

    def get_monthly_pocket_money(self):
        return Decimal(self.monthly_pocket_money) if self.monthly_pocket_money else None

    def get_savings_goal(self):
        return Decimal(self.savings_goal) if self.savings_goal else None

    statements = db.relationship("Statements", backref=db.backref("user"), passive_deletes=True)

    def __repr__(self) -> str:
        return "<Id:%s>" % (str(self.id))

class ExpenseCategory(db.Model):
    __tablename__ = "expense_category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return "<Category:%s>" % (self.name)

class SavingsGoal(db.Model):
    __tablename__ = "savings_goal"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.String(20), nullable=False)  # Store as string
    current_amount = db.Column(db.String(20), nullable=False, default='0.00')  # Store as string
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    user = db.relationship("User", backref=db.backref("goals", lazy=True))

    def get_target_amount(self):
        return Decimal(self.target_amount) if self.target_amount else None

    def get_current_amount(self):
        return Decimal(self.current_amount) if self.current_amount else None

    def __repr__(self) -> str:
        return "<Goal:%s>" % (self.name)



class VisitorStats(db.Model):
    __tablename__ = "visitor_stats"
    id = db.Column(db.Integer, primary_key=True)
    browser = db.Column(db.String(100))
    device = db.Column(db.String(100))
    operating_system = db.Column(db.String(100))
    is_bot = db.Column(db.Boolean())
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))


class Statements(db.Model):
    __tablename__ = "statements"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    operation_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    statement_id = db.Column(db.String(50), nullable=False, unique=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        return "<Id:%s>"%(str(self.id))