from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, Task, User
from app.schemas import AuthOut, LoginInput, ProjectCreate, ProjectOut, RegisterInput, TaskCreate, TaskListOut, TaskOut, TaskStatus, TaskUpdate, UserOut
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api")

def get_owned_project(db: Session, project_id: int, user_id: int) -> Project:
    project = db.scalar(select(Project).where(Project.id == project_id, Project.owner_id == user_id))
    if project is None: raise HTTPException(status_code=404, detail="Project not found")
    return project

def get_owned_task(db: Session, task_id: int, user_id: int) -> Task:
    task = db.scalar(select(Task).join(Project).where(Task.id == task_id, Project.owner_id == user_id))
    if task is None: raise HTTPException(status_code=404, detail="Task not found")
    return task

def project_out(db: Session, project: Project) -> ProjectOut:
    count = db.scalar(select(func.count(Task.id)).where(Task.project_id == project.id)) or 0
    return ProjectOut(id=project.id, name=project.name, description=project.description, owner_id=project.owner_id, created_at=project.created_at, updated_at=project.updated_at, task_count=count)

@router.get("/health")
def health(): return {"status": "ok"}

@router.post("/auth/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    user = User(name=payload.name, email=str(payload.email).lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit(); db.refresh(user)
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409, detail="Email is already registered")
    return AuthOut(user=UserOut.model_validate(user), token=create_access_token(user.id))

@router.post("/auth/login", response_model=AuthOut)
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthOut(user=UserOut.model_validate(user), token=create_access_token(user.id))

@router.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)): return current_user

@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.scalars(select(Project).where(Project.owner_id == current_user.id).order_by(Project.updated_at.desc())).all()
    return [project_out(db, p) for p in projects]

@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = Project(name=payload.name.strip(), description=payload.description.strip(), owner_id=current_user.id)
    db.add(project); db.commit(); db.refresh(project)
    return project_out(db, project)

@router.get("/projects/{project_id}", response_model=ProjectOut)
def project_detail(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return project_out(db, get_owned_project(db, project_id, current_user.id))

@router.get("/projects/{project_id}/tasks", response_model=TaskListOut)
def list_tasks(project_id: int, status_filter: TaskStatus | None = Query(default=None, alias="status"), page: int = Query(default=1, ge=1), limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_owned_project(db, project_id, current_user.id)
    filters = [Task.project_id == project_id]
    if status_filter: filters.append(Task.status == status_filter.value)
    total = db.scalar(select(func.count(Task.id)).where(*filters)) or 0
    tasks = db.scalars(select(Task).where(*filters).order_by(Task.updated_at.desc()).offset((page - 1) * limit).limit(limit)).all()
    return TaskListOut(tasks=tasks, pagination={"page": page, "limit": limit, "total": total, "pages": ceil(total / limit) if total else 0})

@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(project_id: int, payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_owned_project(db, project_id, current_user.id)
    task = Task(project_id=project_id, title=payload.title.strip(), description=payload.description.strip(), priority=payload.priority.value, status=TaskStatus.TODO.value, due_date=payload.due_date)
    db.add(task); db.commit(); db.refresh(task)
    return task

@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_owned_task(db, task_id, current_user.id)
    changes = payload.model_dump(exclude_unset=True)
    if not changes: raise HTTPException(status_code=400, detail="At least one field is required")
    for key, value in changes.items():
        if key in {"title", "description", "status", "priority"} and value is None:
            raise HTTPException(status_code=422, detail=f"{key} cannot be null")
        if key in {"status", "priority"} and value is not None: value = value.value
        setattr(task, key, value)
    db.commit(); db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = get_owned_task(db, task_id, current_user.id)
    db.delete(task); db.commit()
