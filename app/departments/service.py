from sqlalchemy.orm import Session
from app.departments.models import Department
from app.departments.schemas import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    """Service layer for department operations."""

    @staticmethod
    def create_department(db: Session, dept: DepartmentCreate) -> Department:
        """Create a new department."""
        db_dept = Department(
            department_code=dept.department_code,
            name=dept.name,
            description=dept.description,
            status=dept.status,
        )
        db.add(db_dept)
        db.commit()
        db.refresh(db_dept)
        return db_dept

    @staticmethod
    def get_department(db: Session, dept_id: int) -> Department | None:
        """Get department by ID."""
        return db.query(Department).filter(Department.id == dept_id).first()

    @staticmethod
    def get_department_by_code(db: Session, code: str) -> Department | None:
        """Get department by code."""
        return db.query(Department).filter(Department.department_code == code).first()

    @staticmethod
    def list_departments(db: Session, skip: int = 0, limit: int = 100) -> list[Department]:
        """List all departments."""
        return db.query(Department).offset(skip).limit(limit).all()

    @staticmethod
    def update_department(
        db: Session, dept_id: int, dept_update: DepartmentUpdate
    ) -> Department | None:
        """Update a department."""
        db_dept = db.query(Department).filter(Department.id == dept_id).first()
        if not db_dept:
            return None
        
        update_data = dept_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dept, key, value)
        
        db.commit()
        db.refresh(db_dept)
        return db_dept

    @staticmethod
    def delete_department(db: Session, dept_id: int) -> bool:
        """Delete a department."""
        db_dept = db.query(Department).filter(Department.id == dept_id).first()
        if not db_dept:
            return False
        
        db.delete(db_dept)
        db.commit()
        return True
