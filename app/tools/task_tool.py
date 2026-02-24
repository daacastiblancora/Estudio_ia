from langchain_core.tools import tool
from app.core.database import get_sync_engine
from app.models.sql_schemas import Task
from sqlmodel import Session, select
import json


@tool
def create_task(title: str, description: str = "", assigned_to: str = "", priority: str = "media") -> str:
    """
    Creates a new task/to-do item and saves it to the database.
    Use this when the user asks to create a task, reminder, action item, or to-do.
    Args:
        title: Short title of the task
        description: Detailed description of what needs to be done
        assigned_to: Person responsible (optional)
        priority: Priority level - 'alta', 'media', or 'baja' (default: media)
    """
    if priority not in ("alta", "media", "baja"):
        priority = "media"

    task = Task(
        title=title,
        description=description,
        assigned_to=assigned_to if assigned_to else None,
        priority=priority,
        status="pendiente",
    )

    engine = get_sync_engine()
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    result = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "priority": task.priority,
        "status": task.status,
        "message": f"✅ Tarea '{title}' creada exitosamente (ID: {task.id})",
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def list_tasks(status: str = "pendiente") -> str:
    """
    Lists tasks from the database filtered by status.
    Use this when the user asks to see pending tasks, to-dos, or action items.
    Args:
        status: Filter by status - 'pendiente', 'en_progreso', 'completada', or 'todas'
    """
    engine = get_sync_engine()
    with Session(engine) as session:
        if status == "todas":
            stmt = select(Task).order_by(Task.created_at.desc())
        else:
            stmt = select(Task).where(Task.status == status).order_by(Task.created_at.desc())

        tasks = session.exec(stmt).all()

    if not tasks:
        return f"No hay tareas con estado '{status}'."

    task_list = []
    for t in tasks:
        task_list.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "assigned_to": t.assigned_to,
            "priority": t.priority,
            "status": t.status,
            "created_at": t.created_at.isoformat(),
        })

    return json.dumps(task_list, ensure_ascii=False)


tools = [create_task, list_tasks]
