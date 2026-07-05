import csv
import io
from typing import Optional

from app.repositories import ApplicationRepository


class ExportService:
    def export_applications_csv(self, user_id: int, status: Optional[str] = None) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "application_id",
                "status",
                "company",
                "title",
                "location",
                "match_score",
                "application_url",
                "manual_review_confirmed",
                "manual_submission_confirmed",
                "notes",
            ]
        )

        for application in ApplicationRepository.list_for_user(user_id, status=status):
            writer.writerow(
                [
                    application.id,
                    application.status,
                    application.job.company,
                    application.job.title,
                    application.job.location,
                    application.job.match_score,
                    application.job.application_url,
                    application.manual_review_confirmed,
                    application.manual_submission_confirmed,
                    application.notes,
                ]
            )

        return output.getvalue()
