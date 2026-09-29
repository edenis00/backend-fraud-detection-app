from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.departments.service import DepartmentService
from app.departments.schemas import DepartmentCreate, DepartmentUpdate, DepartmentResponse

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/departments", tags=["departments"])


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    dept: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new department (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create departments",
        )
    
    existing = DepartmentService.get_department_by_code(db, dept.department_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department code already exists",
        )
    
    return DepartmentService.create_department(db, dept)


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a department by ID."""
    dept = DepartmentService.get_department(db, dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return dept


@router.get("", response_model=list[DepartmentResponse])
def list_departments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all departments."""
    return DepartmentService.list_departments(db, skip=skip, limit=limit)


@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    dept_update: DepartmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a department (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update departments",
        )
    
    dept = DepartmentService.update_department(db, dept_id, dept_update)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a department (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete departments",
        )
    
    success = DepartmentService.delete_department(db, dept_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
