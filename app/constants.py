APPLICATION_STATUSES = [
    ("saved", "Saved"),
    ("review_pending", "Review Pending"),
    ("ready_for_manual_apply", "Ready For Manual Apply"),
    ("applied", "Applied"),
    ("interviewing", "Interviewing"),
    ("offer", "Offer"),
    ("rejected", "Rejected"),
    ("archived", "Archived"),
]

JOB_SOURCE_TYPES = [
    ("manual", "Manual"),
    ("link", "Link"),
    ("csv", "CSV"),
    ("api", "API"),
]

API_PROVIDER_CHOICES = [
    ("generic_json", "Generic JSON"),
    ("greenhouse", "Greenhouse"),
    ("lever", "Lever"),
]

COMMON_APPLICATION_QUESTIONS = [
    "Why are you interested in this role?",
    "Why are you a strong fit for this position?",
    "What is one gap you would close quickly in this role?",
    "Anything else the recruiter should know before your application review?",
]
