from sqlalchemy import (
    Column, String, Text, Date, Boolean, Integer, Numeric,
    ForeignKey, ARRAY, Computed, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

# this is what's on the CV header
class Person(Base):
    __tablename__ = "person"
    person_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    professional_title = Column(String)
    institution = Column(String)
    department = Column(String)
    faculty = Column(String)
    email = Column(String)
    phone= Column(String)
    office_address = Column(String)


class CV(Base):
    __tablename__ = "cv"
    cv_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    prepared_on = Column(Date)
    cv_tree = Column(JSONB, nullable=False)
    cv_text = Column(Text)
    cv_tsv = Column(TSVECTOR, Computed("to_tsvector('english', cv_text)", persisted=True))
    __table_args__ = ( Index('ix_cv_tsv', cv_tsv, postgresql_using='gin'),)

class Education(Base):
    __tablename__ = "education"
    education_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    category = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    qualification = Column(String)
    specialization = Column(String)
    institution = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    supervisors = Column(ARRAY(String))
    description = Column(Text)

class Appointment(Base):
    __tablename__ = "appointment"
    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    office_type = Column(String)
    office_name = Column(String)
    division = Column(String)
    department = Column(String)
    faculty = Column(String)
    institution = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    appointment_type = Column(String)
    description = Column(Text) #embed this?


class Award(Base):
    __tablename__ = "award"
    award_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    category = Column(String)
    geographic_scope = Column(String)
    nomination_status = Column(String)
    title = Column(String)
    role = Column(String)
    organization = Column(String)
    specialty = Column(String)
    description = Column(Text) #embed this?
    total_amount = Column(Numeric)
    currency = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

class GrantFunding(Base):
    __tablename__ = "grant_funding"
    grant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    peer_reviewed = Column(Boolean)
    status = Column(String)
    role = Column(String)
    title = Column(String)
    funding_source = Column(String)
    program = Column(String)
    grant_number = Column(String)
    principal_investigator = Column(String)
    collaborators = Column(ARRAY(String))
    amount = Column(Numeric)
    currency = Column(String)
    funding_type = Column(String)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)

#search openalex for the paper?
class Publication(Base):
    __tablename__ = "publication"
    publication_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    pub_type = Column(String)
    peer_reviewed = Column(Boolean)
    status = Column(String)
    title = Column(Text)
    journal = Column(String)
    publisher = Column(String)
    volume = Column(String)
    issue = Column(String)
    pages = Column(String)
    publication_date = Column(Date)
    url = Column(String)
    impact_factor = Column(Numeric)
    authors = Column(ARRAY(Text))
    trainee = Column(Boolean)
    role = Column(String)
    citation = Column(String)

class Presentation(Base):
    __tablename__ = "presentation"
    presentation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    scope = Column(String)
    type = Column(String)
    role = Column(String)
    title = Column(String)
    event = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    date = Column(Date)
    presenters = Column(ARRAY(String))
    abstract = Column(Text)
    url = Column(String)


class Teaching(Base):
    __tablename__ = "teaching"
    teaching_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    title = Column(String)
    primary_audience = Column(String)
    faculty = Column(String)
    department = Column(String)
    division = Column(String)
    institution = Column(String)
    description = Column(Text)
    impact = Column(Text)

class Supervision(Base):
    __tablename__ = "supervision"
    supervision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    supervisory_role = Column(Text)
    audience = Column(String)
    student_name = Column(String)
    graduate_unit = Column(String)
    institution = Column(String)
    project_title = Column(String)
    supervisors = Column(ARRAY(String))
    collaborators = Column(ARRAY(String))
    completed_year = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)

#creative professional activity
class CPAActivity(Base):
    __tablename__ = "cpa_activity"
    cpa_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    category = Column(String)
    title = Column(String)
    description = Column(Text)
    impact = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)

class Membership(Base):
    __tablename__ = "membership"
    membership_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role = Column(String)
    institution = Column(String)
    membership_number = Column(String)

class AdministrativeService(Base):
    __tablename__ = "administrative_service"
    service_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    geographic_scope = Column(String)
    organization = Column(String)
    committee_name = Column(String)
    role = Column(String)
    faculty = Column(String)
    department = Column(String)
    division = Column(String)
    street = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    primary_audience = Column(String)
    educational_administration = Column(Boolean)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)


class EditorialRole(Base):
    __tablename__ = "editorial_role"
    editorial_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role = Column(String)
    title = Column(String)
    number_of_reviews = Column(Integer)


class JournalReview(Base):
    __tablename__ = "journal_review"
    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role = Column(String)
    journal_title = Column(String)
    number_of_reviews = Column(Integer)


class GrantReview(Base):
    __tablename__ = "grant_review"
    grant_review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role = Column(String)
    institution = Column(String)
    funding_organization = Column(String)
    number_of_reviews = Column(Integer)


class PresentationReview(Base):
    __tablename__ = "presentation_review"
    presentation_review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role = Column(String)
    conference_title = Column(String)
    organization = Column(String)
    number_of_reviews = Column(Integer)
