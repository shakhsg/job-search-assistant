from app.constants import COMMON_APPLICATION_QUESTIONS
from app.extensions import db
from app.repositories import ApplicationRepository
from app.services.scoring import MatchingEngine
from app.utils.text import lines_to_list, to_multiline_bullets


class MaterialGenerator:
    def __init__(self) -> None:
        self.matching_engine = MatchingEngine()

    def generate_for_job(self, user, job):
        application = ApplicationRepository.get_or_create(user.id, job.id)
        profile = user.profile
        if not profile:
            raise ValueError("Complete the profile before generating materials.")

        if not job.parsed_data:
            raise ValueError("Parse the job description before generating materials.")

        self.matching_engine.refresh_job(profile, job)
        details = job.score_details or {}

        application.resume_draft = self._build_resume(profile, job, details)
        application.cover_letter_draft = self._build_cover_letter(profile, job, details)
        application.screening_answers = self._build_answers(profile, job, details)
        application.truthfulness_notes = self._build_truthfulness_notes(details)
        application.review_checklist = [
            "Confirm every company, date, and title matches your real background.",
            "Remove any bullet that feels overstated or unsupported.",
            "Customize the greeting and final paragraph before sending.",
            "Review application answers for tone, compensation, and work authorization accuracy.",
            "Submit only after your final review and explicit confirmation.",
        ]
        application.review_ready = True
        application.status = "review_pending"
        application.manual_review_confirmed = False
        application.manual_submission_confirmed = False

        db.session.add(application)
        db.session.commit()
        return application

    def _build_resume(self, profile, job, details: dict) -> str:
        skills = details.get("overlap_skills", [])[:8]
        highlights = self._pick_relevant_items(lines_to_list(profile.experience_highlights), job)
        achievements = self._pick_relevant_items(lines_to_list(profile.achievements), job)

        sections = [
            f"{profile.full_name or 'Candidate'}",
            profile.headline or "Tailored Resume Draft",
            f"Target Role: {job.title} at {job.company}",
            "",
            "Summary",
            profile.summary or "Add a short summary to make this draft stronger.",
            "",
            "Relevant Skills",
            to_multiline_bullets(skills or lines_to_list(profile.core_skills)[:8] or ["Add verified skills to your profile."]),
            "",
            "Relevant Highlights",
            to_multiline_bullets(highlights or ["Add experience highlights to tailor this section honestly."]),
            "",
            "Selected Achievements",
            to_multiline_bullets(achievements or ["Add measurable achievements from your real work."]),
            "",
            "Education & Certifications",
            to_multiline_bullets(lines_to_list(profile.education) + lines_to_list(profile.certifications) or ["Add education or certifications if relevant."]),
        ]
        return "\n".join(sections).strip()

    def _build_cover_letter(self, profile, job, details: dict) -> str:
        strengths = details.get("strengths", [])[:3]
        gaps = details.get("gaps", [])[:1]

        body = [
            "Dear Hiring Team,",
            "",
            f"I am applying for the {job.title} role at {job.company}. What stands out to me is the opportunity to contribute to work that aligns with my background in {profile.headline or 'the areas listed in my profile'}.",
            "",
            f"My experience includes {profile.summary or 'the verified experience documented in my profile'}.",
            "",
        ]

        if strengths:
            body.append(f"Based on the job description, my strongest overlap appears to be: {', '.join(strengths)}.")
            body.append("")

        if gaps:
            body.append(f"I also want to be transparent about one area I would address quickly if selected: {gaps[0]}.")
            body.append("")

        body.extend(
            [
                "I would welcome the chance to discuss how my real experience and learning plan fit the role.",
                "",
                "Sincerely,",
                profile.full_name or "Candidate",
            ]
        )
        return "\n".join(body).strip()

    def _build_answers(self, profile, job, details: dict) -> list[dict]:
        overlap = details.get("overlap_skills", [])[:5]
        gaps = details.get("gaps", [])[:2]
        answers = []

        for question in COMMON_APPLICATION_QUESTIONS:
            if "interested" in question.lower():
                answer = (
                    f"I am interested in {job.title} at {job.company} because the role emphasizes "
                    f"{', '.join(job.parsed_data.get('keywords', [])[:3]) or 'work that matches my target direction'}. "
                    f"My interest is strongest where the responsibilities align with my documented experience."
                )
            elif "strong fit" in question.lower():
                answer = (
                    f"My strongest fit comes from verified overlap in {', '.join(overlap) or 'the skills listed in my profile'}. "
                    "I would keep my application focused on that proven experience rather than stretching into claims I cannot support."
                )
            elif "gap" in question.lower():
                answer = (
                    f"One area I would close quickly is {gaps[0] if gaps else 'any requirement where the job asks for deeper depth than my current profile shows'}. "
                    "I would be direct about my current level and outline how I would ramp up."
                )
            else:
                answer = (
                    f"I can share concise examples from my background in {profile.summary or 'my profile'} and confirm my "
                    f"work authorization status as {profile.work_authorization or 'not yet provided in the profile'}."
                )
            answers.append({"question": question, "answer": answer})

        answer_bank = lines_to_list(profile.answer_bank)
        if answer_bank:
            answers.append(
                {
                    "question": "Profile answer bank reminders",
                    "answer": "; ".join(answer_bank[:4]),
                }
            )

        return answers

    def _build_truthfulness_notes(self, details: dict) -> str:
        notes = [
            "This draft uses only information stored in your profile and parsed from the job description.",
            "Review every statement before submitting anything manually.",
        ]
        for gap in details.get("gaps", [])[:3]:
            notes.append(f"Check this possible gap: {gap}")
        for unknown in details.get("unknowns", [])[:2]:
            notes.append(f"Unknown to verify: {unknown}")
        return "\n".join(f"- {note}" for note in notes)

    def _pick_relevant_items(self, items: list[str], job) -> list[str]:
        if not items:
            return []

        keywords = {item.lower() for item in job.parsed_data.get("keywords", [])}
        ranked = sorted(
            items,
            key=lambda item: sum(keyword in item.lower() for keyword in keywords),
            reverse=True,
        )
        return ranked[:6]
