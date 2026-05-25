from sqlalchemy import (
    Column, String, Text, Date, Boolean, Integer, Numeric,
    ForeignKey, ARRAY, Computed, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

# this is what's on the CV header it's just contact information
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
    updated_at=Column(Date)

#this is the whole cv, stored as text and tsvector for keyword search
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
    start_date = Column(Date)
    end_date=Column(Date, nullable=True)
    type = Column(String)
    department=Column(String, nullable=True)
    division=Column(String, nullable=True)
    institution = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    supervisors = Column(ARRAY(String))
    description = Column(Text) #sometimes there are descriptions like thesis work etc.

class Employment(Base):
    __tablename__ = "employment"
    appointment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    office_held = Column(String)
    office_name = Column(String)
    division = Column(String)
    department = Column(String)
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
    start_date=Column(Date)
    end_date=Column(Date)
    awarded=Column(Boolean)
    type=Column(String)
    scope=Column(String)
    amount=Column(Numeric)
    currency=Column(String)
    role=Column(String)
    institution=Column(String)
    description = Column(Text)


#search openalex for the paper?
class Publication(Base):
    __tablename__ = "publication"
    publication_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    title=Column(String)
    date=Column(Date)
    venue=Column(String)
    issue=Column(String)
    authors=Column(String) # This would be a nightmare to normalize, we can think of ways to search for the publication if published to get structured info
    published=Column(Boolean)
    submitter=Column(Boolean)
    reviewed=Column(Boolean)
    type=Column(String)
    trainee=Column(String)
    role=Column(String)

class Presentation(Base):
    __tablename__ = "presentation"
    presentation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    title = Column(String)
    date = Column(Date)
    organizer = Column(String)
    city = Column(String)
    province = Column(String)
    country = Column(String)
    presenters = Column(String) #same as above and now we do not have the ability to search for most of these things unless we get an agent but that also
    #is not that reliable
    scope = Column(String)
    type = Column(String)
    presented = Column(Boolean)

class Funding(Base):
    __tablename__ = "funding"
    grant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date=Column(Date)
    end_date=Column(Date)
    role=Column(String)
    source=Column(String)
    program=Column(String)
    grant_number=Column(String) #it's not always a number
    collaborators=Column(String) #same as authors
    amount=Column(Numeric)
    currency=Column(String)
    declined=Column(Boolean)
    peer_reviewed=Column(Boolean)
    type=Column(String)
    description=Column(Text)


class Teaching(Base):
    __tablename__ = "teaching"
    teaching_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    audience=Column(String)
    faculty=Column(String)
    department=Column(String)
    division=Column(String)
    institution=Column(String)
    description=Column(Text)
    impact=Column(String)

class Supervision(Base):
    __tablename__ = "supervision"
    supervision_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start=Column(Date)
    end=Column(Date)
    audience=Column(String)
    name=Column(String)
    primary=Column(Boolean)
    role=Column(String)
    description=Column(Text)


class Review(Base):
    __tablename__ = "review"
    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    organization=Column(String)
    role = Column(String)
    type = Column(String)
    number_of_reviews = Column(Integer)

class Association(Base):
    __tablename__ = "association"
    association_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role=Column(String)
    member_number=Column(String) #might include letters etc.


class Administration(Base):
    __tablename__ = "administration"
    service_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    role=Column(String)
    committee_name=Column(String)
    organization=Column(String)
    scope=Column(String)

class IntellectualProperty(Base):
    __tablename__ = "intellectual_property"
    intellectual_property_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    date=Column(Date)
    no=Column(String)
    state=Column(String)
    country=Column(String)
    joint_holders=Column(String)
    type=Column(String)


class Creative(Base):
    __tablename__ = "creative"
    creative_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    title=Column(String)
    description = Column(Text)
    impact=Column(String)
    type=Column(String)

class Media(Base):
    __tablename__ = "media"
    media_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    date=Column(Date)
    role=Column(String)
    topic=Column(String)
    program=Column(String)
    network=Column(String)
    city=Column(String)
    state=Column(String)
    country=Column(String)
    scope=Column(String)

#this one contains free text items so creating a ts vector for keyword searches
class Profile:
    __tablename__ = "profile"
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.person_id"))
    research_statement=Column(Text)
    teaching_philosophy=Column(Text)
    creative=Column(Text)
    other=Column(Text)
    research_tsv = Column(TSVECTOR, Computed("to_tsvector('english', research_statement)", persisted=True))
    teaching_tsv = Column(TSVECTOR, Computed("to_tsvector('english', teaching_philosophy)", persisted=True))
    creative_tsv = Column(TSVECTOR, Computed("to_tsvector('english', creative)", persisted=True))
    other_tsv = Column(TSVECTOR, Computed("to_tsvector('english', other)", persisted=True))
    __table_args__ = (Index('ix_research_tsv', research_tsv, postgresql_using='gin'),
                      Index('ix_teaching_tsv', teaching_tsv, postgresql_using='gin'),
                      Index('ix_creative_tsv', creative_tsv, postgresql_using='gin'),
                      Index('ix_other_tsv', other_tsv, postgresql_using='gin'),)



#TODO for profile we might want to include embeddings, similarly for paper, presentation and some other classes if we want to search
# for people who are working on similar things