
DEFAULT_PROMPT_TEMPLATE = """Extract all entities of type '{section_type}' from the supplied CV section.

Use only information explicitly supported by the text.
Do not infer missing information.
Use null when a field cannot be determined.
Return all distinct items.

CV section:
{text}
"""

SECTION_PROMPTS: dict[str, str] = {
    # ---------------------------------------------------------------------------
    # Contact Information
    # ---------------------------------------------------------------------------
    "contact_information": """Extract person's contact details and personal identity information from this CV section.

Key Instructions:
- Split full names into `first_name` and `last_name`[cite: 1].
- Extract titles, honorifics, and academic degrees explicitly associated with the person (e.g., "Dr", "Professor", "MD", "PhD") into a list under `title`[cite: 1].
- Extract institutional affiliation (`organization`), `department`, and physical mailing details (`address`, `city`, `state`, `country`, `postal_code`)[cite: 1].
- Separate communications into `telephone`, `cellphone`, `fax_no`, and `email`[cite: 1].
- Do not infer contact details not explicitly written[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Education
    # ---------------------------------------------------------------------------
    "education": """Extract all education, formal academic training, qualifications, residency, and fellowship items.

Key Instructions:
- For each item, capture start and end dates/years (`start`, `end`)[cite: 1].
- Classify the degree or training level under `type` (e.g., "BSc", "MSc", "PhD", "MD", "Residency", "Fellowship", "Certification")[cite: 1].
- Capture the `institution`, `department`, `division`, and location (`city`, `state`, `country`)[cite: 1].
- Populate `supervisor` only when a supervisor, advisor, or mentor is explicitly associated with that specific educational program[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Employment
    # ---------------------------------------------------------------------------
    "employment": """Extract all employment history, professional appointments, and job positions.

Key Instructions:
- Capture start and end dates/years (`start`, `end`)[cite: 1].
- Capture job title, academic rank, or position held under `office_held`[cite: 1].
- Record the employing `institution`, `department`, and specific unit/group (`office_name`)[cite: 1].
- Categorize `type` if stated (e.g., "faculty", "staff", "trainee", "clinical", "research")[cite: 1].
- Set `current` to true ONLY if the position is explicitly identified as ongoing or current. Return null if end date is absent without explicit confirmation of current status[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Award
    # ---------------------------------------------------------------------------
    "award": """Extract all awards, honours, distinctions, scholarships, and recognitions.

Key Instructions:
- Record start and end dates/years (`start`, `end`)[cite: 1].
- Capture award `name`, granting `institution`, category `type` (e.g., "teaching", "research"), and a brief `description`[cite: 1].
- Assign geographic `scope` strictly using one of: "local", "regional", "national", "international"[cite: 1].
- Extract monetary `amount` as a floating-point number without currency symbols, and store currency code separately under `currency`[cite: 1].
- Set `awarded` to false if explicitly listed as nominated but not received. Return null if unstated[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Publication
    # ---------------------------------------------------------------------------
    "publication": """Extract all publication entries (articles, books, book chapters, monographs, policy documents).

Key Instructions:
- Extract full `title`, `date`/year, publication `venue` (journal/publisher), `volume`, `issue`, and `page_range`[cite: 1].
- Preserve original author order in `authors` list[cite: 1].
- Classify `type` strictly using one of: "article", "book", "book_edited", "book_chapter", "monograph", "report_policy_document", "other"[cite: 1].
- Set `published` to false for work marked as unpublished, submitted, or in preparation[cite: 1].
- Set `submitted` to true ONLY if explicitly stated as submitted[cite: 1].
- Set `reviewed` to true ONLY if peer-review status is explicitly mentioned (do not infer from journal name)[cite: 1].
- Set `trainee` to true ONLY if explicitly designated as a trainee publication in the text[cite: 1].
- Capture explicit impact factor (`impact_factor`) and subject's author role (`role`) if written[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Presentation
    # ---------------------------------------------------------------------------
    "presentation": """Extract all presentations, invited lectures, keynotes, and presented abstracts.

Key Instructions:
- Capture presentation `title`, `date`, `organizer`/event, listed `presenters`, and location (`city`, `state`, `country`)[cite: 1].
- Categorize `type` strictly as either "invited lecture or presentation" or "presented abstract"[cite: 1].
- Assign geographic `scope` using: "local", "regional", "national", "international"[cite: 1].
- Set `presented` to true if the CV subject delivered it, or false if another speaker is explicitly stated[cite: 1].
- Set `trainee` to true ONLY if explicitly noted as a trainee presentation[cite: 1].
- Set `published` to true ONLY if explicitly identified as published in proceedings[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Funding
    # ---------------------------------------------------------------------------
    "funding": """Extract all research grants, funding awards, salary support, and trainee funding.

Key Instructions:
- Extract start and end years (`start`, `end`)[cite: 1].
- Capture funding `source` (funder name), `program`, `grant_number`, and `description`[cite: 1].
- Capture subject's `role` (e.g., "PI", "co-PI", "co-investigator", "collaborator") and list named `collaborators`[cite: 1].
- Categorize `type` strictly using: "research_grant", "salary_support", "trainee_support", "other"[cite: 1].
- Extract numerical funding `amount` without currency symbols, and set `currency` string separately[cite: 1].
- Set `declined` to true ONLY if explicitly stated as declined[cite: 1].
- Set `peer_reviewed` to true ONLY if explicitly identified as peer-reviewed[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Teaching
    # ---------------------------------------------------------------------------
    "teaching": """Extract all teaching activities, course instruction, lecturing, and curriculum development.

Key Instructions:
- Capture activity duration (`start`, `end` dates/years)[cite: 1].
- Extract target `audience` level (e.g., "undergraduate", "graduate", "medical school", "residency", "continuing education")[cite: 1].
- Capture organizational structure: `faculty`, `department`, `division`, and `institution`[cite: 1].
- Extract course/teaching `description` and explicitly stated `impact` or outcome[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Supervision
    # ---------------------------------------------------------------------------
    "supervision": """Extract all mentorship, student supervision, and trainee advisory roles.

Key Instructions:
- Record supervision period (`start`, `end`)[cite: 1].
- Capture `name` of the person supervised and their `audience` level (e.g., "undergraduate", "PhD student", "postdoctoral fellow")[cite: 1].
- Capture subject's supervisory `role` (e.g., "committee member", "research supervisor", "co-supervisor")[cite: 1].
- Set `primary` to true ONLY if explicitly named as primary/principal supervisor[cite: 1].
- Include any additional context under `description`[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Peer Review
    # ---------------------------------------------------------------------------
    "peer_review": """Extract all peer-review activities, editorial board memberships, and journal reviewing.

Key Instructions:
- Capture timeframe (`start`, `end`)[cite: 1].
- Extract target `organization` (journal, publisher, or grant agency)[cite: 1].
- Record `role` (e.g., "reviewer", "editor", "editorial board member")[cite: 1].
- Record material `type` reviewed (e.g., "journal article", "grant", "abstract")[cite: 1].
- Record `number_of_reviews` ONLY if explicitly stated in text (do not estimate)[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Association
    # ---------------------------------------------------------------------------
    "association": """Extract all professional society memberships and organization affiliations.

Key Instructions:
- Capture active dates (`start`, `end`)[cite: 1].
- Record exact professional association `name`[cite: 1].
- Record leadership or membership `role` within the association if explicitly stated[cite: 1].
- Capture explicit membership `number` if provided[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Administration
    # ---------------------------------------------------------------------------
    "administration": """Extract all administrative service roles, committee work, and institutional leadership.

Key Instructions:
- Capture timeframe (`start`, `end`)[cite: 1].
- Extract leadership `role`, `committee_name`, and governing `organization`[cite: 1].
- Assign geographic `scope` using: "local", "regional", "national", "international"[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Intellectual Property
    # ---------------------------------------------------------------------------
    "intellectual_property": """Extract all patents, trademarks, copyrights, disclosures, and technology licenses.

Key Instructions:
- Capture relevant filing/grant `date` and registration/patent `number`[cite: 1].
- Capture geographic region (`state`, `country`)[cite: 1].
- Categorize `type` strictly using: "patent", "trademark", "copyright", "disclosure", "license"[cite: 1].
- List all co-inventors or `joint_holders` and record item `description`[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Creative
    # ---------------------------------------------------------------------------
    "creative": """Extract creative, professional practice, and innovation activities.

Key Instructions:
- Capture activity period (`start`, `end`)[cite: 1].
- Extract activity `title`, detailed `description`, and explicitly stated `impact`[cite: 1].
- Categorize `type` strictly using: "innovation", "contribution", "exemplary"[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Media
    # ---------------------------------------------------------------------------
    "media": """Extract media appearances, press features, interviews, and public commentary.

Key Instructions:
- Capture appearance `date` and subject's `role` (e.g., "interviewee", "expert", "guest")[cite: 1].
- Record discussed `topic`, `program` name, broadcasting `network`, and location (`city`, `state`, `country`)[cite: 1].
- Assign geographic `scope` using: "local", "regional", "national", "international"[cite: 1].

CV section:
{text}
""",

    # ---------------------------------------------------------------------------
    # Profile
    # ---------------------------------------------------------------------------
    "profile": """Extract narrative profile statements, philosophies, and visions.

Key Instructions:
- Extract full text narrative into the corresponding field without summarizing[cite: 1]:
  - `research_statement`: Research vision, philosophy, or narrative[cite: 1].
  - `teaching_philosophy_summary`: Teaching philosophy and summary[cite: 1].
  - `creative`: Narrative describing creative/professional practices[cite: 1].
  - `other`: Personal or general narrative statements that do not fit above[cite: 1].

CV section:
{text}
""",
}