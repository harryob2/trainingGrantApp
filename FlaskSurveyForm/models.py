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

DATABASE_URL = "sqlite:///training_forms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
    training_type = Column(String, nullable=False)
    trainer_name = Column(String)
    supplier_name = Column(String)
    location_type = Column(String, nullable=False)
    location_details = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    training_hours = Column(Float)
    trainees_data = Column(Text)
    submission_date = Column(DateTime, default=func.now())
    approved = Column(Boolean, default=False)
    concur_claim = Column(String)
    travel_cost = Column(Float, default=0)
    food_cost = Column(Float, default=0)
    materials_cost = Column(Float, default=0)
    other_cost = Column(Float, default=0)
    other_expense_description = Column(Text)
    course_cost = Column(Float, default=0)
    training_description = Column(Text, nullable=False)
    submitter = Column(String)
    created_at = Column(DateTime, default=func.now())
    ida_class = Column(String)
    attachments = relationship(
        "Attachment", back_populates="training_form", cascade="all, delete-orphan"
    )

    def to_dict(self, include_costs: bool = False) -> Dict[str, Any]:
        """Convert TrainingForm to dictionary with optional cost fields."""
        result = {
            "id": self.id,
            "training_type": self.training_type,
            "trainer_name": self.trainer_name,
            "supplier_name": self.supplier_name,
            "location_type": self.location_type,
            "location_details": self.location_details,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "training_hours": self.training_hours,
            "trainees_data": self.trainees_data,
            "submission_date": (
                self.submission_date.isoformat() if self.submission_date else None
            ),
            "approved": bool(self.approved),
            "submitter": self.submitter,
            "ida_class": self.ida_class,
            "training_description": self.training_description,
        }
        
        if include_costs:
            result.update({
                "travel_cost": float(self.travel_cost or 0),
                "food_cost": float(self.food_cost or 0),
                "materials_cost": float(self.materials_cost or 0),
                "other_cost": float(self.other_cost or 0),
                "course_cost": float(self.course_cost or 0),
                "concur_claim": self.concur_claim,
                "other_expense_description": self.other_expense_description,
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
    area = Column(String)
    training_name = Column(String)
    qty_staff_attending = Column(String)
    training_desc = Column(String)
    challenge_lvl = Column(String)
    skill_impact = Column(String)
    evaluation_method = Column(String)
    ida_class = Column(String)
    training_type = Column(String)
    training_hours = Column(Float)
    supplier_name = Column(String)
    course_cost = Column(Float, default=0)


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(
        Integer, ForeignKey("training_forms.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String, nullable=False)
    description = Column(String)
    training_form = relationship("TrainingForm", back_populates="attachments")


class Admin(Base):
    __tablename__ = "admins"
    email = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)


def _apply_training_form_filters(query, search_term="", date_from=None, date_to=None, 
                                training_type=None, approval_status=None):
    """Apply common filters to TrainingForm queries."""
    if search_term:
        like_term = f"%{search_term}%"
        query = query.filter(
            (TrainingForm.trainer_name.like(like_term))
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
            trainer_name=form_data.get("trainer_name"),
            training_hours=form_data.get("training_hours"),
            supplier_name=form_data.get("supplier_name"),
            location_type=form_data["location_type"],
            location_details=form_data.get("location_details"),
            start_date=parse_date(form_data["start_date"]),
            end_date=parse_date(form_data["end_date"]),
            trainees_data=form_data.get("trainees_data"),
            approved=form_data.get("approved", False),
            concur_claim=form_data.get("concur_claim"),
            travel_cost=form_data.get("travel_cost", 0),
            food_cost=form_data.get("food_cost", 0),
            materials_cost=form_data.get("materials_cost", 0),
            other_cost=form_data.get("other_cost", 0),
            other_expense_description=form_data.get("other_expense_description"),
            course_cost=form_data.get("course_cost", 0),
            training_description=form_data["training_description"],
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
