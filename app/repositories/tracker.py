from typing import Optional

from app.extensions import db
from app.models import Application


class ApplicationRepository:
    @staticmethod
    def list_for_user(user_id: int, status: Optional[str] = None) -> list[Application]:
        query = Application.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Application.updated_at.desc(), Application.created_at.desc()).all()

    @staticmethod
    def get_owned(application_id: int, user_id: int) -> Optional[Application]:
        return Application.query.filter_by(id=application_id, user_id=user_id).first()

    @staticmethod
    def get_or_create(user_id: int, job_id: int) -> Application:
        application = Application.query.filter_by(user_id=user_id, job_id=job_id).first()
        if application:
            return application

        application = Application(user_id=user_id, job_id=job_id)
        db.session.add(application)
        db.session.commit()
        return application
