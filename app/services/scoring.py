from app.extensions import db
from app.utils.text import lines_to_list, unique_lowered


class MatchingEngine:
    def score(self, profile, job) -> tuple[int, str, dict]:
        parsed = job.parsed_data or {}
        profile_skills = {item.lower() for item in lines_to_list(profile.core_skills)}
        target_roles = {item.lower() for item in lines_to_list(profile.target_roles)}
        preferred_locations = {item.lower() for item in lines_to_list(profile.preferred_locations)}
        must_haves = {item.lower() for item in lines_to_list(profile.must_have_keywords)}
        avoid_keywords = {item.lower() for item in lines_to_list(profile.avoid_keywords)}

        job_skills = {item.lower() for item in parsed.get("skills", [])}
        title = (job.title or "").lower()
        description = (job.description_raw or "").lower()
        location = (job.location or parsed.get("work_mode") or "").lower()

        overlap = sorted(job_skills & profile_skills)
        missing_skills = sorted(job_skills - profile_skills)
        strengths: list[str] = []
        gaps: list[str] = []
        unknowns: list[str] = []

        if job_skills:
            skill_score = round(50 * (len(overlap) / max(len(job_skills), 1)))
            if overlap:
                strengths.append(f"Skill overlap: {', '.join(overlap[:5])}")
            if missing_skills:
                gaps.append(f"Potential skill gaps: {', '.join(missing_skills[:5])}")
        else:
            skill_score = 25
            unknowns.append("No explicit skill list was extracted from the job description.")

        title_hits = [role for role in target_roles if role in title]
        title_score = 20 if title_hits else (10 if target_roles else 8)
        if title_hits:
            strengths.append(f"Title alignment with targets: {', '.join(title_hits[:3])}")
        elif target_roles:
            gaps.append("The job title does not clearly match the target roles in your profile.")
        else:
            unknowns.append("No target roles were added to the profile.")

        if not preferred_locations:
            location_score = 6
            unknowns.append("No preferred locations were listed in the profile.")
        elif any(place in location for place in preferred_locations) or "remote" in location:
            location_score = 10
            strengths.append("Location preference appears to fit.")
        else:
            location_score = 3
            gaps.append("Location may be outside your preferred geography.")

        seniority = parsed.get("seniority", "mid")
        years = profile.years_experience or 0
        experience_score = 10
        if seniority == "junior" and years > 8:
            experience_score = 6
            gaps.append("Role may be more junior than your experience level.")
        elif seniority == "senior" and years < 4:
            experience_score = 4
            gaps.append("Years of experience may be light for a senior-level role.")
        elif seniority == "director+" and years < 8:
            experience_score = 2
            gaps.append("Experience may not yet match a director-level scope.")
        else:
            strengths.append(f"Experience looks plausible for a {seniority} role.")

        must_have_hits = [keyword for keyword in must_haves if keyword in description or keyword in title]
        must_have_score = 10 if not must_haves else round(10 * len(must_have_hits) / max(len(must_haves), 1))
        if must_haves and must_have_hits:
            strengths.append(f"Must-have keywords found: {', '.join(must_have_hits[:5])}")
        elif must_haves:
            gaps.append("Some profile must-haves were not found in the job description.")

        avoid_hits = [keyword for keyword in avoid_keywords if keyword in description or keyword in title]
        avoid_penalty = 0
        if avoid_hits:
            avoid_penalty = 10
            gaps.append(f"Red-flag keywords found: {', '.join(avoid_hits[:5])}")

        total = max(0, min(100, skill_score + title_score + location_score + experience_score + must_have_score - avoid_penalty))

        summary = "Strong match" if total >= 75 else "Promising but review gaps" if total >= 55 else "Proceed carefully"
        details = {
            "components": {
                "skills": skill_score,
                "title": title_score,
                "location": location_score,
                "experience": experience_score,
                "must_haves": must_have_score,
                "avoid_penalty": avoid_penalty,
            },
            "overlap_skills": overlap,
            "missing_skills": missing_skills,
            "strengths": unique_lowered(strengths),
            "gaps": unique_lowered(gaps),
            "unknowns": unique_lowered(unknowns),
        }
        return total, summary, details

    def refresh_job(self, profile, job, *, commit: bool = True) -> None:
        score, summary, details = self.score(profile, job)
        job.match_score = score
        job.match_summary = summary
        job.score_details = details
        if commit:
            db.session.add(job)
            db.session.commit()

    def refresh_all_for_user(self, user, *, commit: bool = True) -> None:
        if not user.profile:
            return
        for job in user.jobs.all():
            self.refresh_job(user.profile, job, commit=False)
        if commit:
            db.session.commit()
