from typing import Optional

from app.extensions import db
from app.models import Job


class JobRepository:
    @staticmethod
    def list_for_user(user_id: int) -> list[Job]:
        return (
            Job.query.filter_by(user_id=user_id)
            .order_by(Job.updated_at.desc(), Job.created_at.desc())
            .all()
        )

    @staticmethod
    def get_owned(job_id: int, user_id: int) -> Optional[Job]:
        return Job.query.filter_by(id=job_id, user_id=user_id).first()

    @staticmethod
    def upsert(user_id: int, payload: dict) -> Job:
        job = None
        job_id = payload.get("id")
        external_id = payload.get("external_id") or ""
        source_url = payload.get("source_url") or ""
        provider_name = payload.get("provider_name") or ""

        if job_id:
            job = Job.query.filter_by(id=job_id, user_id=user_id).first()

        if job is None and external_id and provider_name:
            job = Job.query.filter_by(
                user_id=user_id,
                external_id=external_id,
                provider_name=provider_name,
            ).first()

        if job is None and source_url:
            job = Job.query.filter_by(user_id=user_id, source_url=source_url).first()

        if job is None:
            job = Job(user_id=user_id)

        for key, value in payload.items():
            setattr(job, key, value)

        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def delete(job: Job) -> None:
        db.session.delete(job)
        db.session.commit()
