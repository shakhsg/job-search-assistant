from app.extensions import db
from app.models import Profile


class ProfileRepository:
    @staticmethod
    def get_or_create(user) -> Profile:
        if user.profile:
            return user.profile

        profile = Profile(user=user, email=user.email)
        db.session.add(profile)
        db.session.commit()
        return profile
