from enum import Enum
from pydantic import BaseModel, Field


llm_prompt="""Extract all entities of the requested type from the supplied CV section.

Use only information explicitly supported by the text.
Do not infer missing information.
Use null when a field cannot be determined.
Return all distinct items.

CV section:
{text}

"""


class GeographicScope(str, Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"


class PublicationType(str, Enum):
    ARTICLE = "article"
    BOOK = "book"
    BOOK_EDITED = "book_edited"
    BOOK_CHAPTER = "book_chapter"
    MONOGRAPH = "monograph"
    REPORT_POLICY_DOCUMENT = "report_policy_document"
    OTHER = "other"


class PresentationType(str, Enum):
    INVITED_LECTURE_OR_PRESENTATION = "invited lecture or presentation"
    PRESENTED_ABSTRACT = "presented abstract"


class FundingType(str, Enum):
    RESEARCH_GRANT = "research_grant"
    SALARY_SUPPORT = "salary_support"
    TRAINEE_SUPPORT = "trainee_support"
    OTHER = "other"


class CreativeType(str, Enum):
    INNOVATION = "innovation"
    CONTRIBUTION = "contribution"
    EXEMPLARY_PRACTICE = "exemplary"


class IntellectualPropertyType(str, Enum):
    PATENT = "patent"
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"
    DISCLOSURE = "disclosure"
    LICENSE = "license"


# ---------------------------------------------------------------------------
# Contact information
# ---------------------------------------------------------------------------

class ContactInformation(BaseModel):
    first_name: str | None = Field(
        default=None,
        description="First name of the person."
    )

    last_name: str | None = Field(
        default=None,
        description="Last name of the person."
    )

    title: list[str] | None = Field(
        default=None,
        description=(
            "Titles and degrees explicitly associated with the person, "
            "such as Dr, Professor, MD, PhD, MHSc. Return each title or "
            "degree as a separate list item."
        )
    )

    organization: str | None = Field(
        default=None,
        description="Name of the person's organization or institution."
    )

    department: str | None = Field(
        default=None,
        description="Department associated with the person's position."
    )

    address: str | None = Field(
        default=None,
        description="Street address."
    )

    city: str | None = Field(
        default=None,
        description="City."
    )

    state: str | None = Field(
        default=None,
        description="State or province."
    )

    country: str | None = Field(
        default=None,
        description="Country."
    )

    postal_code: str | None = Field(
        default=None,
        description="Postal or ZIP code."
    )

    telephone: str | None = Field(
        default=None,
        description="Telephone number, including extension if explicitly provided."
    )

    cellphone: str | None = Field(
        default=None,
        description="Cellphone or mobile telephone number."
    )

    fax_no: str | None = Field(
        default=None,
        description="Fax number."
    )

    email: str | None = Field(
        default=None,
        description="Email address."
    )


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

class EducationItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the education, training, or qualification."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the education, training, or qualification."
    )

    type: str | None = Field(
        default=None,
        description=(
            "Type of degree, qualification, or training, such as MD, PhD, "
            "BSc, MSc, certification, residency, fellowship, or postdoctoral fellowship."
        )
    )

    department: str | None = Field(
        default=None,
        description="Department associated with the education or training."
    )

    division: str | None = Field(
        default=None,
        description="Division associated with the education or training, if explicitly stated."
    )

    institution: str | None = Field(
        default=None,
        description="Institution where the education or training occurred."
    )

    city: str | None = Field(
        default=None,
        description="City of the institution."
    )

    state: str | None = Field(
        default=None,
        description="State or province of the institution."
    )

    country: str | None = Field(
        default=None,
        description="Country of the institution."
    )

    supervisor: str | None = Field(
        default=None,
        description=(
            "Name of the supervisor, advisor, or training supervisor. "
            "Only populate when explicitly associated with this education or training."
        )
    )


class Education(BaseModel):
    education: list[EducationItem] = Field(
        default_factory=list,
        description="All education and training items identified in the CV chunk."
    )


# ---------------------------------------------------------------------------
# Employment
# ---------------------------------------------------------------------------

class EmploymentItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the employment or appointment."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the employment or appointment."
    )

    department: str | None = Field(
        default=None,
        description="Department of the employing institution."
    )

    city: str | None = Field(
        default=None,
        description="City of the employment."
    )

    state: str | None = Field(
        default=None,
        description="State or province of the employment."
    )

    country: str | None = Field(
        default=None,
        description="Country of the employment."
    )

    institution: str | None = Field(
        default=None,
        description="Name of the employing institution or organization."
    )

    office_held: str | None = Field(
        default=None,
        description="Job title, academic rank, or position held."
    )

    office_name: str | None = Field(
        default=None,
        description="Name of the office, unit, or organizational group, if explicitly stated."
    )

    type: str | None = Field(
        default=None,
        description=(
            "Type of appointment, such as faculty, staff, trainee, "
            "clinical, research, or another explicitly stated appointment type."
        )
    )

    current: bool | None = Field(
        default=None,
        description=(
            "Whether the position is explicitly identified as current or ongoing. "
            "Return null when current status cannot be determined. Do not infer "
            "current status merely because an end date is absent."
        )
    )


class Employment(BaseModel):
    employment: list[EmploymentItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Awards
# ---------------------------------------------------------------------------

class AwardItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year associated with the award."
    )

    end: str | None = Field(
        default=None,
        description="End date or year associated with the award."
    )

    name: str | None = Field(
        default=None,
        description="Name of the award, honour, or distinction."
    )

    awarded: bool | None = Field(
        default=None,
        description=(
            "Whether the person actually received the award. "
            "Return false when the CV explicitly states that the person "
            "was nominated but did not receive it. Return null when the "
            "award status is not explicitly stated."
        )
    )

    type: str | None = Field(
        default=None,
        description=(
            "Type of award if explicitly stated, such as distinction, "
            "teaching award, research award, trainee award, or similar."
        )
    )

    scope: GeographicScope | None = Field(
        default=None,
        description="Geographic scope of the award."
    )

    amount: float | None = Field(
        default=None,
        description="Monetary amount associated with the award, without currency."
    )

    currency: str | None = Field(
        default=None,
        description="Currency of the award amount."
    )

    role: str | None = Field(
        default=None,
        description="Individual or team role explicitly associated with the award."
    )

    institution: str | None = Field(
        default=None,
        description="Institution or organization that granted the award."
    )

    description: str | None = Field(
        default=None,
        description="Brief description of the award if explicitly provided."
    )


class Awards(BaseModel):
    award: list[AwardItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Publications
# ---------------------------------------------------------------------------

class PublicationItem(BaseModel):
    title: str | None = Field(
        default=None,
        description="Full title of the publication."
    )

    date: str | None = Field(
        default=None,
        description="Publication date or year as stated in the CV."
    )

    venue: str | None = Field(
        default=None,
        description="Journal, book publisher, or other publication venue."
    )

    volume: str | None = Field(
        default=None,
        description="Journal or book volume, if explicitly stated."
    )

    issue: str | None = Field(
        default=None,
        description="Journal issue number, not a topical issue or subject."
    )

    authors: list[str] | None = Field(
        default=None,
        description="Authors listed for the publication, preserving their CV order."
    )

    page_range: str | None = Field(
        default=None,
        description="Page range or article page information."
    )

    published: bool | None = Field(
        default=None,
        description=(
            "Whether the work has been published. Return false for works "
            "explicitly identified as unpublished, submitted, or in preparation. "
            "Return null when publication status is unclear."
        )
    )

    submitted: bool | None = Field(
        default=None,
        description=(
            "Whether the work is explicitly identified as submitted for publication. "
            "Do not infer submission from other information."
        )
    )

    reviewed: bool | None = Field(
        default=None,
        description=(
            "Whether the publication is explicitly identified as peer reviewed. "
            "Do not infer peer-review status from the journal, publication type, "
            "or normal academic practice."
        )
    )

    type: PublicationType | None = Field(
        default=None,
        description="Type of publication."
    )

    trainee: bool | None = Field(
        default=None,
        description=(
            "Whether the CV explicitly identifies this as a trainee publication "
            "or associates the publication with the CV subject's trainee work. "
            "Do not infer this from author position, publication date, degree dates, "
            "or the fact that the work was performed at a university."
        )
    )

    impact_factor: float | None = Field(
        default=None,
        description=(
            "Journal impact factor, only when explicitly stated in the CV. "
            "Do not look it up or infer it."
        )
    )

    role: str | None = Field(
        default=None,
        description=(
            "The CV subject's explicitly stated role in the publication, "
            "such as first author, co-first author, senior author, corresponding "
            "author, co-principal author, or other stated role."
        )
    )


class Publications(BaseModel):
    publication: list[PublicationItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Presentations
# ---------------------------------------------------------------------------

class PresentationItem(BaseModel):
    title: str | None = Field(
        default=None,
        description="Title of the presentation."
    )

    date: str | None = Field(
        default=None,
        description="Date or year of the presentation."
    )

    organizer: str | None = Field(
        default=None,
        description="Organization, conference, institution, or event organizer."
    )

    presenters: list[str] | None = Field(
        default=None,
        description="Presenters explicitly listed for the presentation."
    )

    city: str | None = Field(
        default=None,
        description="City where the presentation occurred."
    )

    state: str | None = Field(
        default=None,
        description="State or province where the presentation occurred."
    )

    country: str | None = Field(
        default=None,
        description="Country where the presentation occurred."
    )

    contribution: str | None = Field(
        default=None,
        description="Description of the person's contribution, if explicitly stated."
    )

    trainee: bool | None = Field(
        default=None,
        description=(
            "Whether the presentation is explicitly identified as a trainee "
            "presentation or associated with trainee work. Do not infer this "
            "from the person's career stage."
        )
    )

    scope: GeographicScope | None = Field(
        default=None,
        description="Geographic scope of the presentation."
    )

    presented: bool | None = Field(
        default=None,
        description=(
            "Whether the CV subject was the person who presented the work. "
            "Return false when another presenter is explicitly identified. "
            "Return null when the presenter cannot be determined."
        )
    )

    published: bool | None = Field(
        default=None,
        description=(
            "Whether the presentation is explicitly identified as having "
            "been published as a paper or publication. Do not infer publication "
            "from the existence of an abstract."
        )
    )

    type: PresentationType | None = Field(
        default=None,
        description="Type of presentation."
    )


class Presentations(BaseModel):
    presentation: list[PresentationItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Funding
# ---------------------------------------------------------------------------

class FundingItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the funding period."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the funding period."
    )

    role: str | None = Field(
        default=None,
        description=(
            "The person's role in the funding, such as PI, co-PI, collaborator, "
            "co-investigator, or another explicitly stated role."
        )
    )

    source: str | None = Field(
        default=None,
        description="Organization or individual providing the funding."
    )

    program: str | None = Field(
        default=None,
        description="Specific government, institutional, or private funding program."
    )

    grant_number: str | None = Field(
        default=None,
        description="Grant number, application number, or award number."
    )

    collaborators: list[str] | None = Field(
        default=None,
        description="Named collaborators associated with the funding."
    )

    amount: float | None = Field(
        default=None,
        description="Funding amount as a number without currency."
    )

    currency: str | None = Field(
        default=None,
        description="Currency of the funding amount."
    )

    declined: bool | None = Field(
        default=None,
        description=(
            "Whether the funding was explicitly declined. "
            "Do not infer this from the absence of an award."
        )
    )

    peer_reviewed: bool | None = Field(
        default=None,
        description=(
            "Whether the funding opportunity or award was explicitly "
            "identified as peer reviewed."
        )
    )

    type: FundingType | None = Field(
        default=None,
        description="Type of funding."
    )

    description: str | None = Field(
        default=None,
        description="Description of the project or work funded."
    )


class Funding(BaseModel):
    funding: list[FundingItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Teaching
# ---------------------------------------------------------------------------

class TeachingItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the teaching activity."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the teaching activity."
    )

    audience: str | None = Field(
        default=None,
        description=(
            "Audience or educational level, such as undergraduate, graduate, "
            "medical school, residency, or continuing education."
        )
    )

    faculty: str | None = Field(
        default=None,
        description="Faculty or school within the institution."
    )

    department: str | None = Field(
        default=None,
        description="Department within the institution."
    )

    division: str | None = Field(
        default=None,
        description="Division within the department or institution."
    )

    institution: str | None = Field(
        default=None,
        description="Institution where the teaching occurred."
    )

    description: str | None = Field(
        default=None,
        description=(
            "Description of the course, class, curriculum, tutoring, "
            "or other teaching activity."
        )
    )

    impact: str | None = Field(
        default=None,
        description=(
            "Explicitly stated impact, improvement, development, or outcome "
            "of the teaching activity."
        )
    )


class Teaching(BaseModel):
    teaching: list[TeachingItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Supervision
# ---------------------------------------------------------------------------

class SupervisionItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the supervision."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the supervision."
    )

    audience: str | None = Field(
        default=None,
        description=(
            "Level or type of person supervised, such as undergraduate, "
            "medical student, graduate student, postgraduate, fellow, "
            "research trainee, or other explicitly stated level."
        )
    )

    name: str | None = Field(
        default=None,
        description="Name of the specific person being supervised."
    )

    primary: bool | None = Field(
        default=None,
        description=(
            "Whether the CV explicitly identifies the CV subject as the "
            "primary or principal supervisor. Return null when this cannot "
            "be determined."
        )
    )

    role: str | None = Field(
        default=None,
        description=(
            "Role in the supervision, such as committee member, clinical "
            "supervisor, research supervisor, co-supervisor, or another stated role."
        )
    )

    description: str | None = Field(
        default=None,
        description="Other relevant description of the supervision."
    )


class Supervision(BaseModel):
    supervision: list[SupervisionItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Peer review
# ---------------------------------------------------------------------------

class PeerReviewItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the peer-review activity."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the peer-review activity."
    )

    organization: str | None = Field(
        default=None,
        description="Journal, publisher, funding agency, organization, or other body."
    )

    role: str | None = Field(
        default=None,
        description=(
            "Role performed by the person, such as reviewer, editor, "
            "editorial board member, or committee member."
        )
    )

    type: str | None = Field(
        default=None,
        description=(
            "Type of material or activity reviewed, such as journal article, "
            "grant, presentation, abstract, or other explicitly stated type."
        )
    )

    number_of_reviews: int | None = Field(
        default=None,
        description=(
            "Number of reviews explicitly stated for this activity or organization. "
            "Do not estimate or infer the number."
        )
    )


class PeerReview(BaseModel):
    peer_review: list[PeerReviewItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Associations
# ---------------------------------------------------------------------------

class AssociationItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of membership."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of membership."
    )

    name: str | None = Field(
        default=None,
        description="Name of the professional association."
    )

    role: str | None = Field(
        default=None,
        description="Role within the association, if explicitly stated."
    )

    number: str | None = Field(
        default=None,
        description="Membership number, if explicitly provided."
    )


class Associations(BaseModel):
    association: list[AssociationItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Administration
# ---------------------------------------------------------------------------

class AdministrationItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year of the administrative activity."
    )

    end: str | None = Field(
        default=None,
        description="End date or year of the administrative activity."
    )

    role: str | None = Field(
        default=None,
        description="Role within the committee, group, or organization."
    )

    committee_name: str | None = Field(
        default=None,
        description="Name of the committee or administrative group."
    )

    organization: str | None = Field(
        default=None,
        description="Organization or institution that the committee belongs to."
    )

    scope: GeographicScope | None = Field(
        default=None,
        description="Geographic scope of the administrative activity."
    )


class Administration(BaseModel):
    administration: list[AdministrationItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Intellectual property
# ---------------------------------------------------------------------------

class IntellectualPropertyItem(BaseModel):
    date: str | None = Field(
        default=None,
        description="Filing, registration, disclosure, or other relevant date."
    )

    number: str | None = Field(
        default=None,
        description="Patent, copyright, trademark, disclosure, license, or registration number."
    )

    state: str | None = Field(
        default=None,
        description="State or province associated with the intellectual property."
    )

    country: str | None = Field(
        default=None,
        description="Country associated with the intellectual property."
    )

    joint_holders: list[str] | None = Field(
        default=None,
        description="Names of other explicitly identified joint holders."
    )

    type: IntellectualPropertyType | None = Field(
        default=None,
        description="Type of intellectual property."
    )

    description: str | None = Field(
        default=None,
        description="Description of the intellectual property."
    )


class IntellectualProperty(BaseModel):
    intellectual_property: list[IntellectualPropertyItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Creative / professional activities
# ---------------------------------------------------------------------------

class CreativeItem(BaseModel):
    start: str | None = Field(
        default=None,
        description="Start date or year."
    )

    end: str | None = Field(
        default=None,
        description="End date or year, if applicable."
    )

    title: str | None = Field(
        default=None,
        description="Title or name of the innovation, contribution, or practice."
    )

    description: str | None = Field(
        default=None,
        description="Description of the innovation, contribution, or practice."
    )

    impact: str | None = Field(
        default=None,
        description="Explicitly stated impact or outcome."
    )

    type: CreativeType | None = Field(
        default=None,
        description="Type of creative or professional activity."
    )


class Creative(BaseModel):
    creative: list[CreativeItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

class MediaItem(BaseModel):
    date: str | None = Field(
        default=None,
        description="Date or year of the media appearance."
    )

    role: str | None = Field(
        default=None,
        description="Role in the appearance, such as interviewee, expert, guest, or featured person."
    )

    topic: str | None = Field(
        default=None,
        description="Topic discussed or presented."
    )

    program: str | None = Field(
        default=None,
        description="Name of the broadcast, program, publication, or media outlet program."
    )

    network: str | None = Field(
        default=None,
        description="Name of the broadcasting network or media organization."
    )

    city: str | None = Field(
        default=None,
        description="City of the appearance, if explicitly stated."
    )

    state: str | None = Field(
        default=None,
        description="State or province of the appearance."
    )

    country: str | None = Field(
        default=None,
        description="Country of the appearance."
    )

    scope: GeographicScope | None = Field(
        default=None,
        description="Geographic scope of the media outlet or appearance."
    )


class Media(BaseModel):
    media: list[MediaItem] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class ProfileItem(BaseModel):
    research_statement: str | None = Field(
        default=None,
        description=(
            "Full narrative text describing the person's research philosophy, "
            "research vision, or research activities."
        )
    )

    teaching_philosophy_summary: str | None = Field(
        default=None,
        description=(
            "Full narrative text describing the person's teaching philosophy "
            "and/or summary of teaching activities."
        )
    )

    creative: str | None = Field(
        default=None,
        description=(
            "Full narrative text describing creative or professional activities."
        )
    )

    other: str | None = Field(
        default=None,
        description=(
            "Other narrative personal statement that does not fit the other "
            "profile categories."
        )
    )

class Profile(BaseModel):
    profile: list[ProfileItem] = Field(
        default_factory=list
    )

class CVSectionType(str, Enum):
    CONTACT_INFORMATION = "contact_information"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    AWARD = "award"
    PUBLICATION = "publication"
    PRESENTATION = "presentation"
    FUNDING = "funding"
    TEACHING = "teaching"
    SUPERVISION = "supervision"
    PEER_REVIEW = "peer_review"
    ASSOCIATION = "association"
    ADMINISTRATION = "administration"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CREATIVE = "creative"
    MEDIA = "media"
    PROFILE = "profile"

class SectionClassification(BaseModel):
    section_type: CVSectionType = Field(
        description=(
            "The CV section category that best describes the supplied "
            "text. Choose the category based on the actual content, "
            "not merely the section heading."
        )
    )

EXTRACTION_MODELS = {
    "contact_information": ContactInformation,
    "education": Education,
    "employment": Employment,
    "award": Awards,
    "publication": Publications,
    "presentation": Presentations,
    "funding": Funding,
    "teaching": Teaching,
    "supervision": Supervision,
    "peer_review": PeerReview,
    "association": Associations,
    "administration": Administration,
    "intellectual_property": IntellectualProperty,
    "creative": Creative,
    "media": Media,
    "profile": Profile,
}