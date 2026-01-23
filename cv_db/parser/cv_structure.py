from enum import Enum
from typing import Optional, Tuple, List, Union
from datetime import date
from dataclasses import dataclass

class CPAType(Enum):
    innovation = "innovation"
    contribution_prof_practice = "prof_practice"
    exemplary_prof_practice = "prof_practice"

class SupervisionScope(Enum):
    multilevel = "multilevel"
    undergraduate = "undergraduate"
    graduate = "graduate"
    postgrad_md= "postgrad_md"
    undergrad_md= "undergrad_md"
    cont="cont"
    faculty_development = "faculty_development"
    public_education = "public_education"
    postdoc= "postdoc"
    research_associate = "research_associate"
    clinical_research_fellow = "clinical_research_fellow"
    other = "other"

class IPType(Enum):
    patent = "patent"
    copyright="copyright"
    license="licence"
    disclosure="disclosure"
    trademark="trademark"

class PubType(Enum):
    journal = "journal"
    editorial="editorial"
    letters_to_the_editor="letters_to_the_editor"
    review="review"
    corrigendum="corrigendum"
    addendum="addendum"
    rapid_communication="rapid_communication"
    book="book"
    book_chapter="book_chapter"
    monograph="monograph"
    other="other"


class GeoScope(Enum):
    international = "international"
    national = "national"
    regional = "regional"
    local = "local"

class AwardType(Enum):
    distinctions = "distinctions"
    teaching = "teaching"
    trainee = "trainee"

class DegreeType(Enum):
    degree = "degree"
    postgrad = "postgrad"
    qualification = "qualification"

class ReviewType(Enum):
    associate="associate"
    journal="journal"
    grant="grant"
    presentation="presentation"

@dataclass
class Institution:
    name:str
    department:Optional[str] = None
    division:Optional[str] = None
    province_state: Optional[str] = None
    city: Optional[str]= None
    state: Optional[str]= None
    county: Optional[str]= None

@dataclass
class Degree:
    start:date
    end: date
    type: DegreeType
    qualification: Optional[str] = None
    degree: Optional[str]= None
    institution:Optional[Institution] = None
    supervisors: Optional[List[str]] = None

@dataclass
class Appointment:
    start:date
    end:date
    institution: Institution
    office_held:Optional[str] = None
    office_name:Optional[str] = None
    type:Optional[str] = None
    description:Optional[str] = None
    current: Optional[bool] = None

@dataclass
class Award:
    start:date
    end:date
    name:str
    awarded:bool #if not awarded assume nominated
    type: AwardType
    scope: Optional[GeoScope] = None
    amount:Optional[float]=None
    currency: Optional[str]= None
    role: Optional[str] = None
    institution: Optional[Institution] = None
    type: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Associations:
    start:date
    end:date
    institution:Institution
    membership_num:Optional[str]=None
    role:Optional[str]=None

@dataclass
class Administration:
    start:date
    end:date
    role:str
    is_education:Optional[bool]=None
    scope:Optional[GeoScope]=None
    committee_name: Optional[str] = None
    faculty: Optional[str] = None
    institution: Optional[Institution] = None
    audience: Optional[str] = None

@dataclass
class PeerReview:
    start:date
    end:date
    institution: Institution
    type: ReviewType
    role:Optional[str]=None
    title:Optional[str]=None
    num_reviews: Optional[int] = None

@dataclass
class Research:
    start:date
    end:date
    institution:Institution
    supervisors:Optional[list[str]] = None
    collaborators:Optional[list[str]] = None
    notes:Optional[str] = None
    is_thesis:bool = False

@dataclass
class Activities:
    activity: Optional[Union[Administration, Associations, PeerReview, Research]]=None

@dataclass
class Profile:
    research_statement: Optional[str]
    teaching_statement: Optional[str]
    creative_professional_statement: Optional[str]

@dataclass
class ResearchFunding:
    start:date
    end:date
    role:str
    name:str
    source: str
    program: Optional[str]
    grant_num: Optional[str]
    pi: Optional[str]
    collaborators:Optional[list[str]] = None
    amount: Optional[float] = None
    currency: Optional[str]= None
    type: Optional[str]= None
    declined: bool = False
    peer_reviewed: Optional[bool] = True
    salary_support: Optional[bool] = None
    trainee_salary: Optional[bool] = None

@dataclass
class Citation:
    title:str
    type: PubType
    year: Optional[str]= None
    month: Optional[str]= None
    date: Optional[str]= None
    publisher: Optional[str]= None
    volumne: Optional[str]= None
    issue: Optional[str]= None
    page_range: Optional[Tuple[int, int]]= None
    published: Optional[bool]= None #if not published, if could be submitted or in prep
    submitted: Optional[bool]= None
    reviewed: Optional[bool]= None
    trainee: Optional[bool]= None
    impact_factor: Optional[float]= None
    role: Optional[str]= None


@dataclass
class IP:
    title:str
    filing_date:date
    number:str
    type: IPType
    state_province:Optional[str]= None
    county:Optional[str]= None
    holder_names: Optional[List[str]]= None
    notes:Optional[str]= None

@dataclass
class Presentation:
    date:date
    title:str
    organizer: Optional[str]= None
    city: Optional[str]= None
    state_province: Optional[str]= None
    county: Optional[str]= None
    presenters: Optional[List[str]]= None
    contribution: Optional[str]= None
    is_trainee: Optional[bool]= None
    scope: GeoScope= GeoScope
    presented: Optional[bool]= None
    published: Optional[bool]= None
    invited: Optional[bool]= None

@dataclass
class MediaAppearance:
    role: str
    date: date
    topic: Optional[str]= None
    program: Optional[str]= None
    network: Optional[str]= None
    city: Optional[str]= None
    state_province: Optional[str]= None
    county: Optional[str]= None
    is_trainee: Optional[bool]= None
    scope: GeoScope= GeoScope

@dataclass
class Presentations:
    presentation: Optional[Presentation]= None

@dataclass
class Supervision:
    start: date
    end: date
    role: str
    name: str
    position: Optional[str]= None
    institution: Optional[Institution]= None
    title: Optional[str]= None
    is_group: Optional[bool]= None
    is_thesis: bool= None
    collaborators: Optional[List[str]]= None
    completed: Optional[bool]= None
    is_primary: Optional[bool]= None
    scope: Optional[SupervisionScope]= None

@dataclass
class Creative:
    start: date
    end: date
    title: Optional[str]= None
    description: Optional[str]= None
    impact: Optional[str]= None
    type: Optional[CPAType]= None

@dataclass
class Course:
    start: date
    end: date
    title: Optional[str]= None
    audience: Optional[SupervisionScope]= None
    institution: Optional[Institution]= None
    description: Optional[str]= None
    impact: Optional[str]= None

@dataclass
class CV:
    first_name: str
    last_name: str
    title: Optional[str]= None
    date_prepared: Optional[date]= None
    office: Optional[Institution]= None
    telephone: Optional[str]= None
    cellphone: Optional[str]= None
    fax: Optional[str]= None
    email: Optional[str]= None
    education: Optional[List[Degree]]= None
    employment: Optional[Appointment]= None
    awards: Optional[List[Award]]= None
    activities: Optional[List[Activities]]= None
    courses: Optional[Course]= None
    profile: Optional[List[Profile]]= None
    funding: Optional[List[ResearchFunding]] = None
    publications: Optional[List[Citation]] = None
    presentations: Optional[List[Presentations]] = None
    ip: Optional[IP]= None
    creatives: Optional[List[Creative]] = None
    supervisions: Optional[List[Supervision]] = None


