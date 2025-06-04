"""
Database models and functions for the training form application.

This module defines the database schema and functions for interacting with the database.
"""

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session
from sqlalchemy.sql import func
from contextlib import contextmanager
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple
import logging

# Import database configuration from config
try:
    from config import DATABASE_URL, USE_SQLITE
    print(f"Using database configuration from config.py: {DATABASE_URL}")
except ImportError:
    # Fallback to default SQLite configuration
    DATABASE_URL = "sqlite:///training_forms.db"
    USE_SQLITE = True
    print("Warning: config.py not found, using default SQLite configuration")

# Create engine with appropriate settings
if USE_SQLITE:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # MariaDB/MySQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False  # Set to True for SQL debugging
    )

SessionLocal = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


@contextmanager
def db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def parse_date(val) -> Optional[date]:
    """Parse date from various formats."""
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except Exception:
            pass
    return None


class TrainingForm(Base):
    __tablename__ = "training_forms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    training_type = Column(String(255), nullable=False)
    training_name = Column(String(255), nullable=False)
    trainer_name = Column(String(255))
    trainer_email = Column(String(255))
    trainer_department = Column(String(255))
    supplier_name = Column(String(255))
    location_type = Column(String(255), nullable=False)
    location_details = Column(String(500))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    training_hours = Column(Float)
    submission_date = Column(DateTime, default=func.now())
    approved = Column(Boolean, default=False)
    concur_claim = Column(String(255))
    course_cost = Column(Float, default=0)
    invoice_number = Column(String(255))
    training_description = Column(Text, nullable=False)
    notes = Column(Text)
    submitter = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    ida_class = Column(String(255))
    attachments = relationship(
        "Attachment", back_populates="training_form", cascade="all, delete-orphan"
    )
    travel_expenses = relationship(
        "TravelExpense", back_populates="training_form", cascade="all, delete-orphan"
    )
    material_expenses = relationship(
        "MaterialExpense", back_populates="training_form", cascade="all, delete-orphan"
    )
    trainees = relationship(
        "Trainee", back_populates="training_form", cascade="all, delete-orphan"
    )

    def to_dict(self, include_costs: bool = False) -> Dict[str, Any]:
        """Convert TrainingForm to dictionary with optional cost fields."""
        result = {
            "id": self.id,
            "training_type": self.training_type,
            "training_name": self.training_name,
            "trainer_name": self.trainer_name,
            "trainer_email": self.trainer_email,
            "trainer_department": self.trainer_department,
            "supplier_name": self.supplier_name,
            "location_type": self.location_type,
            "location_details": self.location_details,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "training_hours": self.training_hours,
            "submission_date": (
                self.submission_date.isoformat() if self.submission_date else None
            ),
            "approved": bool(self.approved),
            "submitter": self.submitter,
            "ida_class": self.ida_class,
            "training_description": self.training_description,
            "notes": self.notes,
            "trainees": [trainee.to_dict() for trainee in self.trainees],
        }
        
        if include_costs:
            result.update({
                "course_cost": float(self.course_cost or 0),
                "invoice_number": self.invoice_number,
                "concur_claim": self.concur_claim,
                "travel_expenses": [expense.to_dict() for expense in self.travel_expenses],
            })
        
        return result

    def update_from_dict(self, form_data: Dict[str, Any]) -> None:
        """Update TrainingForm fields from dictionary."""
        for key, value in form_data.items():
            if hasattr(self, key):
                if key in ("start_date", "end_date"):
                    setattr(self, key, parse_date(value))
                else:
                    setattr(self, key, value)


class TrainingCatalog(Base):
    __tablename__ = "training_catalog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    area = Column(String(255))
    training_name = Column(String(255))
    qty_staff_attending = Column(String(255))
    training_desc = Column(String(500))
    challenge_lvl = Column(String(255))
    skill_impact = Column(String(255))
    evaluation_method = Column(String(255))
    ida_class = Column(String(255))
    training_type = Column(String(255))
    training_hours = Column(Float)
    supplier_name = Column(String(255))
    course_cost = Column(Float, default=0)


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(
        Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    description = Column(Text)
    training_form = relationship("TrainingForm", back_populates="attachments")


class Admin(Base):
    __tablename__ = "admins"
    email = Column(String(255), primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))


class Trainee(Base):
    __tablename__ = "trainees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(
        Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    training_form = relationship("TrainingForm", back_populates="trainees")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Trainee to dictionary."""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TravelExpense(Base):
    __tablename__ = "travel_expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(
        Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False
    )
    travel_date = Column(Date, nullable=False)
    destination = Column(String(255), nullable=False)
    traveler_type = Column(String(255), nullable=False)  # 'trainer' or 'trainee'
    traveler_email = Column(String(255), nullable=False)
    traveler_name = Column(String(255), nullable=False)
    travel_mode = Column(String(255), nullable=False)  # 'mileage', 'rail', 'economy_flight'
    cost = Column(Float)  # for rail/flight
    distance_km = Column(Float)  # for mileage
    created_at = Column(DateTime, default=func.now())
    training_form = relationship("TrainingForm", back_populates="travel_expenses")

    def to_dict(self) -> Dict[str, Any]:
        """Convert TravelExpense to dictionary."""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "travel_date": self.travel_date.isoformat() if self.travel_date else None,
            "destination": self.destination,
            "traveler_type": self.traveler_type,
            "traveler_email": self.traveler_email,
            "traveler_name": self.traveler_name,
            "travel_mode": self.travel_mode,
            "cost": float(self.cost) if self.cost else None,
            "distance_km": float(self.distance_km) if self.distance_km else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MaterialExpense(Base):
    __tablename__ = "material_expenses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(
        Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False
    )
    purchase_date = Column(Date, nullable=False)
    supplier_name = Column(String(255), nullable=False)
    invoice_number = Column(String(255), nullable=False)
    material_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    training_form = relationship("TrainingForm", back_populates="material_expenses")

    def to_dict(self) -> Dict[str, Any]:
        """Convert MaterialExpense to dictionary."""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "supplier_name": self.supplier_name,
            "invoice_number": self.invoice_number,
            "material_cost": float(self.material_cost) if self.material_cost else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def _apply_training_form_filters(query, search_term="", date_from=None, date_to=None, 
                                training_type=None, approval_status=None):
    """Apply common filters to TrainingForm queries."""
    if search_term:
        like_term = f"%{search_term}%"
        query = query.filter(
            (TrainingForm.training_name.like(like_term))
            | (TrainingForm.trainer_name.like(like_term))
            | (TrainingForm.trainer_email.like(like_term))
            | (TrainingForm.supplier_name.like(like_term))
            | (TrainingForm.location_details.like(like_term))
            | (TrainingForm.training_description.like(like_term))
        )
    if date_from:
        query = query.filter(TrainingForm.start_date >= date_from)
    if date_to:
        query = query.filter(TrainingForm.end_date <= date_to)
    if training_type:
        query = query.filter(TrainingForm.training_type == training_type)
    if approval_status:
        if approval_status == "approved":
            query = query.filter(TrainingForm.approved == True)
        elif approval_status == "unapproved":
            query = query.filter(TrainingForm.approved == False)
    return query


def _apply_sorting_and_pagination(query, sort_by="submission_date", sort_order="DESC", page=1, page_size=10):
    """Apply sorting and pagination to queries."""
    if sort_order.upper() == "DESC":
        query = query.order_by(getattr(TrainingForm, sort_by).desc())
    else:
        query = query.order_by(getattr(TrainingForm, sort_by))
    
    if page_size > 0:  # Only apply pagination if page_size > 0
        query = query.offset((page - 1) * page_size).limit(page_size)
    
    return query


def get_admin_by_email(email: str) -> Optional[Dict[str, str]]:
    """Retrieve an admin by their email."""
    with db_session() as session:
        admin = session.query(Admin).filter_by(email=email).first()
        if admin:
            return {
                "email": admin.email,
                "first_name": admin.first_name,
                "last_name": admin.last_name,
            }
        return None


def add_admin(admin_data: Dict[str, str]) -> bool:
    """Add a new admin to the database."""
    with db_session() as session:
        if session.query(Admin).filter_by(email=admin_data["email"]).first():
            return False  # Admin with this email already exists
        admin = Admin(
            email=admin_data["email"],
            first_name=admin_data["first_name"],
            last_name=admin_data["last_name"],
        )
        session.add(admin)
        return True


def create_tables():
    """Create all database tables if they don't exist and insert default admins."""
    Base.metadata.create_all(bind=engine)
    admin_emails = [
        {"email": "harry@test.com", "first_name": "Harry", "last_name": "Test"},
        {
            "email": "harry.obrien@stryker.com",
            "first_name": "Harry",
            "last_name": "O'Brien",
        },
    ]
    with db_session() as session:
        for adm in admin_emails:
            if not session.query(Admin).filter_by(email=adm["email"]).first():
                session.add(Admin(**adm))


def insert_training_form(form_data: Dict[str, Any]) -> int:
    """Insert a new training form into the database."""
    with db_session() as session:
        form = TrainingForm(
            training_type=form_data["training_type"],
            training_name=form_data["training_name"],
            trainer_name=form_data.get("trainer_name"),
            trainer_email=form_data.get("trainer_email"),
            trainer_department=form_data.get("trainer_department"),
            training_hours=form_data.get("training_hours"),
            supplier_name=form_data.get("supplier_name"),
            location_type=form_data["location_type"],
            location_details=form_data.get("location_details"),
            start_date=parse_date(form_data["start_date"]),
            end_date=parse_date(form_data["end_date"]),
            approved=form_data.get("approved", False),
            concur_claim=form_data.get("concur_claim"),
            course_cost=form_data.get("course_cost", 0),
            invoice_number=form_data.get("invoice_number"),
            training_description=form_data["training_description"],
            notes=form_data.get("notes"),
            submitter=form_data.get("submitter"),
            ida_class=form_data.get("ida_class"),
        )
        session.add(form)
        session.flush()
        return form.id


def update_training_form(form_id: int, form_data: Dict[str, Any]) -> bool:
    """Update an existing training form in the database."""
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        if not form:
            return False
        form.update_from_dict(form_data)
        return True


def get_training_form(form_id: int) -> Optional[Dict[str, Any]]:
    """Get a training form by ID"""
    with db_session() as session:
        form = session.query(TrainingForm).filter_by(id=form_id).first()
        return form.to_dict(include_costs=True) if form else None


def get_all_training_forms(
    search_term: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    training_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    sort_by: str = "submission_date",
    sort_order: str = "DESC",
    page: int = 1,
) -> Tuple[List[Dict[str, Any]], int]:
    """Get all training forms with optional filtering and pagination"""
    with db_session() as session:
        query = session.query(TrainingForm)
        query = _apply_training_form_filters(
            query, search_term, date_from, date_to, training_type, approval_status
        )
        total_count = query.count()
        query = _apply_sorting_and_pagination(query, sort_by, sort_order, page)
        forms = query.all()
        return [form.to_dict() for form in forms], total_count


def get_approved_forms_for_export() -> List[Dict[str, Any]]:
    """Get all approved training forms for export, without pagination."""
    with db_session() as session:
        query = session.query(TrainingForm).filter_by(approved=True)
        query = _apply_sorting_and_pagination(query, page_size=0)  # No pagination
        forms = query.all()
        return [form.to_dict(include_costs=True) for form in forms]


def get_user_training_forms(
    submitter_email: str,
    search_term: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    training_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    sort_by: str = "submission_date",
    sort_order: str = "DESC",
    page: int = 1,
) -> Tuple[List[Dict[str, Any]], int]:
    """Get all training forms for a specific user with optional filtering and pagination"""
    with db_session() as session:
        query = session.query(TrainingForm).filter_by(submitter=submitter_email)
        query = _apply_training_form_filters(
            query, search_term, date_from, date_to, training_type, approval_status
        )
        total_count = query.count()
        query = _apply_sorting_and_pagination(query, sort_by, sort_order, page)
        forms = query.all()
        return [form.to_dict() for form in forms], total_count


# Travel Expense CRUD Functions

def insert_travel_expenses(form_id: int, travel_expenses_data: List[Dict[str, Any]]) -> bool:
    """Insert multiple travel expenses for a training form."""
    try:
        with db_session() as session:
            for expense_data in travel_expenses_data:
                expense = TravelExpense(
                    form_id=form_id,
                    travel_date=parse_date(expense_data["travel_date"]),
                    destination=expense_data["destination"],
                    traveler_type=expense_data["traveler_type"],
                    traveler_email=expense_data["traveler_email"],
                    traveler_name=expense_data["traveler_name"],
                    travel_mode=expense_data["travel_mode"],
                    cost=expense_data.get("cost"),
                    distance_km=expense_data.get("distance_km"),
                )
                session.add(expense)
        return True
    except Exception as e:
        logging.error(f"Error inserting travel expenses: {str(e)}")
        return False


def update_travel_expenses(form_id: int, travel_expenses_data: List[Dict[str, Any]]) -> bool:
    """Update travel expenses for a training form by replacing all existing ones."""
    try:
        with db_session() as session:
            # Delete existing travel expenses for this form
            session.query(TravelExpense).filter_by(form_id=form_id).delete()
            
            # Insert new travel expenses
            for expense_data in travel_expenses_data:
                expense = TravelExpense(
                    form_id=form_id,
                    travel_date=parse_date(expense_data["travel_date"]),
                    destination=expense_data["destination"],
                    traveler_type=expense_data["traveler_type"],
                    traveler_email=expense_data["traveler_email"],
                    traveler_name=expense_data["traveler_name"],
                    travel_mode=expense_data["travel_mode"],
                    cost=expense_data.get("cost"),
                    distance_km=expense_data.get("distance_km"),
                )
                session.add(expense)
        return True
    except Exception as e:
        logging.error(f"Error updating travel expenses: {str(e)}")
        return False


def get_travel_expenses(form_id: int) -> List[Dict[str, Any]]:
    """Get all travel expenses for a training form."""
    with db_session() as session:
        expenses = session.query(TravelExpense).filter_by(form_id=form_id).all()
        return [expense.to_dict() for expense in expenses]


def delete_travel_expense(expense_id: int) -> bool:
    """Delete a specific travel expense."""
    try:
        with db_session() as session:
            expense = session.query(TravelExpense).filter_by(id=expense_id).first()
            if expense:
                session.delete(expense)
                return True
            return False
    except Exception as e:
        logging.error(f"Error deleting travel expense: {str(e)}")
        return False


# Material Expense CRUD Functions

def insert_material_expenses(form_id: int, material_expenses_data: List[Dict[str, Any]]) -> bool:
    """Insert multiple material expenses for a training form."""
    try:
        with db_session() as session:
            for expense_data in material_expenses_data:
                expense = MaterialExpense(
                    form_id=form_id,
                    purchase_date=parse_date(expense_data["purchase_date"]),
                    supplier_name=expense_data["supplier_name"],
                    invoice_number=expense_data["invoice_number"],
                    material_cost=expense_data["material_cost"],
                )
                session.add(expense)
        return True
    except Exception as e:
        logging.error(f"Error inserting material expenses: {str(e)}")
        return False


def update_material_expenses(form_id: int, material_expenses_data: List[Dict[str, Any]]) -> bool:
    """Update material expenses for a training form by replacing all existing ones."""
    try:
        with db_session() as session:
            # Delete existing material expenses for this form
            session.query(MaterialExpense).filter_by(form_id=form_id).delete()
            
            # Insert new material expenses
            for expense_data in material_expenses_data:
                expense = MaterialExpense(
                    form_id=form_id,
                    purchase_date=parse_date(expense_data["purchase_date"]),
                    supplier_name=expense_data["supplier_name"],
                    invoice_number=expense_data["invoice_number"],
                    material_cost=expense_data["material_cost"],
                )
                session.add(expense)
        return True
    except Exception as e:
        logging.error(f"Error updating material expenses: {str(e)}")
        return False


def get_material_expenses(form_id: int) -> List[Dict[str, Any]]:
    """Get all material expenses for a training form."""
    with db_session() as session:
        expenses = session.query(MaterialExpense).filter_by(form_id=form_id).all()
        return [expense.to_dict() for expense in expenses]


def delete_material_expense(expense_id: int) -> bool:
    """Delete a specific material expense."""
    try:
        with db_session() as session:
            expense = session.query(MaterialExpense).filter_by(id=expense_id).first()
            if expense:
                session.delete(expense)
                return True
            return False
    except Exception as e:
        logging.error(f"Error deleting material expense: {str(e)}")
        return False


# Trainee CRUD Functions

def insert_trainees(form_id: int, trainees_data: List[Dict[str, Any]]) -> bool:
    """Insert multiple trainees for a training form."""
    try:
        with db_session() as session:
            for trainee_data in trainees_data:
                trainee = Trainee(
                    form_id=form_id,
                    name=trainee_data["name"],
                    email=trainee_data["email"],
                    department=trainee_data.get("department", "Engineering"),
                )
                session.add(trainee)
        return True
    except Exception as e:
        logging.error(f"Error inserting trainees: {str(e)}")
        return False


def update_trainees(form_id: int, trainees_data: List[Dict[str, Any]]) -> bool:
    """Update trainees for a training form by replacing all existing ones."""
    try:
        with db_session() as session:
            # Delete existing trainees for this form
            session.query(Trainee).filter_by(form_id=form_id).delete()
            
            # Insert new trainees
            for trainee_data in trainees_data:
                trainee = Trainee(
                    form_id=form_id,
                    name=trainee_data["name"],
                    email=trainee_data["email"],
                    department=trainee_data.get("department", "Engineering"),
                )
                session.add(trainee)
        return True
    except Exception as e:
        logging.error(f"Error updating trainees: {str(e)}")
        return False


def get_trainees(form_id: int) -> List[Dict[str, Any]]:
    """Get all trainees for a training form."""
    with db_session() as session:
        trainees = session.query(Trainee).filter_by(form_id=form_id).all()
        return [trainee.to_dict() for trainee in trainees]


def delete_trainee(trainee_id: int) -> bool:
    """Delete a specific trainee."""
    try:
        with db_session() as session:
            trainee = session.query(Trainee).filter_by(id=trainee_id).first()
            if trainee:
                session.delete(trainee)
                return True
            return False
    except Exception as e:
        logging.error(f"Error deleting trainee: {str(e)}")
        return False
