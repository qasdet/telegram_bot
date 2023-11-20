import datetime
from multiprocessing import current_process
from sqlalchemy import select, delete, Integer, and_
from sqlalchemy import func
from database import database as db
from model.academic_performance import (
    AcademicPerformance,
    MissedInfo,
    FullAcademicPerformance,
)
from model.admin import Admin
from model.group import Group
from model.student import Student
from model.discipline import Discipline
from model.missed_class import MissedClass


def get_discipline() -> list[Discipline]:
    with db.Session() as session:
        smt = select(Discipline)
        return session.scalar(smt).all()


def get_assigned_group(discipline_id: int) -> list[Group]:
    with db.Session as session:
        discipline = session.get(Discipline, discipline_id)
        return discipline.groups


def get_students(group_id: int) -> list[Student]:
    with db.Session as session:
        smt = select(Student).where(Student.group_id == group_id)
        return session.scalar(smt).all()


def set_all_missed_students(
        group_id: int,
        discipline_id: int,
        is_missed=True,
) -> None:
    session = db.Session()
    group = session.get(Group, group_id)
    current_date = datetime.date.today()
    for student in group.students:
        student.missed.append(
            MissedClass(
                discipline_id=discipline_id,
                date=current_date,
                is_missed=is_missed,
            )
        )
    session.commit()
    session.commit()


def set_all_missed_students(
        group_id: int,
        discipline_id: int,
        is_missed=True,
) -> None:
    session = db.Session()
    group = session.get(Group, group_id)
    current_date = datetime.date.today()
    for student in group.students:
        student.missed.append(
            MissedClass(
                discipline_id=discipline_id,
                date=current_date,
                is_missed=is_missed,
            )
        )
    session.commit()
    session.close()


def set_missed_student(
        student_id: list[int],
        group_id: int,
        discipline_id: int,
) -> None:
    session = db.Session()
    group = session.get(Group, group_id)
    current_date = datetime.date.today()
    for student in group.students:
        is_missed = student.id in student_id
        student.missed.append(
            MissedClass(
                discipline_id=discipline_id,
                date=current_date,
                is_missed=is_missed,
            )
        )



def is_admin(user_telegram_id: int) -> bool:
    with db.Session() as session:
        admin = session.get(Admin, user_telegram_id)
        return admin is not None
