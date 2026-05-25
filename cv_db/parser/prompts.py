sys_classification_prompt = """You are an expert assistant, you goal is to provided structued information from unstructured CV chunks. For a given chunk below indentify the section that it belongs to"""

sys_extraction_prompt = """
You are a precise CV data extraction engine. Your sole function is to extract structured information from CV text and return it as valid JSON.

## Output Rules
- Return ONLY valid JSON. No prose, no markdown, no preamble, no code fences.
- If a field is not found, use null for scalar values and [] for arrays.
- Never hallucinate, infer, or embellish any information not explicitly present in the text.

## Formatting Rules
- Normalize all dates to ISO 8601: YYYY-MM or YYYY if the month is unknown.
- Treat "present", "current", "now", and equivalent terms as a null end date.
- Normalize whitespace: strip leading/trailing spaces, collapse internal multiple spaces.
- Preserve original casing for proper nouns (names, companies, institutions, tools).
- Return all arrays in the order they appear in the source text.
"""

classifiction_prompt = """
You are an expert assistant, you goal is to provided structued information from unstructured CV chunks. For a given chunk below indentify the section that it belongs to

Sections:
- education: degrees, training, academic qualifications, certifications this is the eductaion recieved by the person not mentorship provided, education might include school or on the job training like residency or medical/postdoctoral fellowship 
- employment: positions and appointments, current and past,
- award: honors and distinctions but not certifications for research, leadership or teaching these can come from education institutions, private and public organizations or professional associations,
- publication: journal articles, letters, short articles, books, book chapters peer reviewed and not peer reviewed
- presentation: invited or applied talks, posters and abstracts
- funding: grants, peer reviewed and non peer reviewed, these may include funding that is rejected by the person (not by the funding agency)
- teaching: includes innovations to teaching and improvements in teaching environments or content including course development and courses taught at different levels including tutoring. 
- supervision: mentoring students, graduate, undergraduate and/or medical, this needs to be one on one superivion of a specific person, with names explicitly stated otherwise it's teaching. 
- administration: committee memberships, leadership administrative activities, not including professional associations but in organizational positions
- association: memberships to professional associations past and present, these may include specific roles within the association
- peer_review: peer reviewing activities journals/grants, not items that get peer reviewed by others
- intellectual_property: patents and trademarks granted or submitted
- creative: creative work such as professional innovations or contributions to professional practices, this does not include non-work related creative activities
- media: interviews in news, radio, press or other media outlets, this usually is for lay person or general audience media outlets not scientific or professional organizations
- contact_information: phone, email, office address this is the current contact information of the person not their employment history
- profile: ONLY narrative personal statements that describes philosophy, values and vision in research teaching and professional practice

Each chunk can only belong to one section. Do not alter information. Do not invent or modify section definitions

Return the name of the section only, no explanation, no markdown, no additional comments

Text chunk:

{header}:

{chunk_content}
"""

extraction_prompts = {

    "contact_information": """
    Extract the following information from the chunk of text provided below. This is the contact information section of a CV:

    Your response shold be in the following json format:
    {contact_information:{
    first_name: <first name of the person>, 
    last_name: <last name of the person>, 
    title: <| separate list of titles and degress associated with the person such as Dr, Prof, MD, MHSc etc.>
    organization:<Name of Org>, 
    department:<department>, 
    address:<street adress>, city:city
    state:<state or province>, 
    country:<country>, 
    postal_code:<postal_code>, 
    telephone:<tel no, extension if available>, 
    cellphone:<cell no>, 
    fax_no:<fax no>, email:<email>}}

    Not all the fields might be available in the text chunk, whenever the information is not available do not make up information instead
    fill it with null. 

    Text:
    {text}
    """,

    "education": """
    Extract the following information from the chunk of text provided below. This is the education section of a CV, it contains 
    degrees, training, academic qualifications, certifications this is the eductaion recieved by the person education might include school or on the job training 
    like residency or medical/postdoctoral fellowship. 

    For each education item your response shold be in the following json format:
    {education:[
    {start:<start date>, 
    end:<end date>, 
    type:<type of degree like md, phd certifiation, bsc>, 
    department:<department>, 
    division:<division if applicaple otherwisenull>, 
    institutions:<institution>, 
    city:<city>, 
    state:<state or province>, 
    country:<country>, 
    supervisor:<name of supervisor if applicable AND mentioned>

    Not all the fields might be available in the text chunk, whenever the information is not available do not make up information instead
    fill it with null.

    Text:
    {text}
    """,

    "employment": """

    Extract the following information from the chunk of text provided below. This is the employment section of a CV and includes
    current and past positions, appointments, and roles


    For each employment item your response should be in the following json format:
    {employment:[
    {start:<start date>, 
    end:<end date>, 
    department:<department>, 
    city:<city>, 
    state:<state or province>, 
    country:<country>, 
    institution:<institution name>, 
    office_held:<job title>,
    office_name:<office or unit name if applicable>, 
    type:<appointment type e.g. faculty, staff, trainee>,
    current:<true if explicitly current otherwise false>}]}

    Not all fields may be available. When information is missing, do not infer or fabricate it; use null.    

    Text:
    {text}
    """,


    "award":"""
    
    Extract the following information from the chunk of text provided below. This is the awards section of a CV and includes
    honors and distinctions. Do NOT include certifications or degrees.

    For each award item your response should be in the following json format:
    {award:[
    {start:<start date>, 
    end:<end date>, 
    name:<award name>, 
    awarded:<true if awarded, false if only nominated>,
    type:<award type if stated such as distinction, teaching or trainee awards>, 
    scope:<geographic scope (local, regional, national, international>,
    amount:<monetary amount>, 
    currency:<currency>, 
    role:<individual or team role if stated>,
    institution:<awarding institution>, 
    description:<brief description if stated>}]}

    If a field is not explicitly present, set it to null.

    Text:
    {text}
    """,

"publication": """
    Extract the following information from the chunk of text provided below. This is the publications section of a CV and may include
    peer-reviewed and non–peer-reviewed journal articles, letters, books, and book chapters.

    For each publication your response should be in the following json format:
    {publication:[
    {title:<title of the publication>, 
    date:<publication date>, 
    venue:<journal or publisher>, 
    volume: <journal or book volumne if available>, 
    issue:<journal issue not topic if available>, 
    authors:<| separated list of authors>, 
    page_range:<ranges of pages in book or journal if available>, 
    published: <whether publisher of not, boolean>, 
    submitted: <whether has been submitted for publication, boolean>, 
    reviewed: <whether this is a peer reviewed publication, boolean>, 
    type:<one of the following, article, book, book_edited, book_chapter, monograph, report_policy_document, other>,
    trainee: <whether this is a trainee publication, boolean>, impact_factor:<impact factor of the journal if explicitly stated>, 
    role: <role in the publication, co-principal author, first author etc.>}]

    Do not infer peer-review status unless explicitly stated. Missing fields should be null.

    Text:
    {text}
    """,

"presentation": """
    Extract the following information from the chunk of text provided below. This is the presentations section of a CV and may include
    peer-reviewed and non–peer-reviewed poster presentations, invitied or applied talks, this does not include lay person media appearances

    For each presentation your response should be in the following json format:
    {presentation: [
    title:<title of the presentation>, 
    date:<presentation date>, 
    organizer: <name of the organization, conference and/or insititution>, 
    presenters: <| separated list of presenters>, 
    city: <city where the presentation happened>, 
    state:<state or province where the presentation happened>, 
    country:<country>, 
    contribution : <description of the contirbutions>, 
    trainee: <whether it's a trainee presentation, boolean>, 
    scope:<geographic scope (local, regional, national, international)>,
    presented: <whether the person whose CV this is the presenter>, 
    published:<whether this presetnation was published as a paper, boollean>, 
    type:<one of the following, invited lecture or presentation, presented abstract>}

    Do not infer any of the fields, if they are explicityl stated the values should be null. 

    Text:
    {text}
    """,

"funding": """
    Extract the following information from the chunk of text provided below. This is the funding section of a CV and may include
    research funding awared to the person. The funding may come from government and private organizations, they may or may not be peer reviewed, 
    they may or may not be accepted by the person. 

    For each funding section your response should be in the following json format:
    {funding: [
    {start:<start date>, end:<end date>, 
    role:<role within the funding, pi, co-pi, collaborator etc. needs to be explicity stated>, 
    source:<organization/indivual providing the funding>, 
    program : <if a specific goverment or private program is providing the funding within the organization>, 
    grant_number : <grant application number>, 
    collaborators: <| separated list of collaborators>, 
    amount: <award amount just the number not the currency>, 
    currency:<currency of the amount>, 
    declined:<whether the award was declined, boolean>, 
    peer_reviewed:<whether the funding was peer reviewed, boolean>, 
    type:<one of the following: research_grant, salary_support, trainee_support or other>]
    description: < a description of the project that is funded>}

    If a field is not explicitly present, set it to null.

    Text:
    {text}
    """,

"teaching": """
    Extract the following information from the chunk of text provided below. This section contains all the teaching done by the person. 
    Teaching is about courses developed, taught or being an available mentor in a specific training program this includes tutoring for a class  
    This does not include specific people that the person mentored. 

    For each teaching item your response should be in the following json format:
    {teaching:[{
    start:<start date>, 
    end:<end date>, 
    audience: <the audience for the class, such as undergraduate, graduate, medical school etc.>, 
    faculty: <faculty of the institution where the class is taught if applicable>, 
    department: <department of the institution where the class is taught if applicable>, 
    division: <division of the institution where the class is taught if applicable>, 
    institution: <name of the institution where the class is taught>, 
    description: <description of the class, course or teaching>, 
    impact: <impact, improvement or further development if statated>}]
    }

    If a field is not explicitly present set it to null. 

    Text:
    {text}

    """,

"supervision": """

    Supervision is done with a specific person on a one-on-one basis, these might include masters/phd students, 
    thesis committees, specific project or fellowshipt supervision. A person can be a primary supervisor or a co-supervisor with another person.

    For each item, your response should be in the following json format: 

    {supervision:[{
    start:<start date>, 
    end: <end date>, 
    audience: <the level of supervision for example undergraduate, medical, graduate, post graduate, fellowship, research etc.>
    name: <name of the the student>
    primary: <is the persion primary supervisor, boolean>, 
    role: <role of the person in supervision, like committee member, clinical supervisor, research supervisor or any other description>,
    description: <description of the supervision if applicable, any text that is not realted to other fields go here>,


    Text:
    {text}
    """,


"peer_review":"""
    Extract the following information from the chunk of text provided below. This section contains all the peer reviewing activities that the person has
    participated in. These do not include academic work that person has submittied for peer review. 

    For each item, your response should be in the following json format:
    {peer_review:[{
    start:<start date>, 
    end:<end date>, 
    organization: <name of the organization/journal/publisher etc.>, 
    role: <what they did within the organization editor, reviewer, board member etc.>
    type: <type of review done, journal, grant, presentation etc.>}, 
    number_of_reviews: < number of reviews conducted, if not explicitly stated set to null>]
    }

    If a field is not explicitly present set it to null. 

    Text:
    {text}    
    """,

"association": """
    Extract the following information from the chunk of text provided below. This section contains all the memberships to different professional 
    associations that the person belongs to. 

    For each item your response should be in the following json format:
    {association:[{
    start:<start date>, 
    end:<end date>, 
    name: <name of the association>, 
    role: <role within the association>, 
    number: <membership number if available>}]}

    If a filed is not explicityly present, set it to null.

    Text:
    {text}
    """,

"administration": """
    Extract the following information from the chunk of text provided below. This is the administrative activities section of the CV and 
    includes committee activities that are administrative. They may include activites in the place of work or other professional associations. 
    This section includes additional work done not just membership such has being members of committes or other leadership activities. 

    For each item your response should be in the following json format:
    {administration:[{
    start:<start date>, 
    end:<end date>, 
    role: <role withing the group/organization>, 
    comittee_name: <name of the committee>, 
    organization: <name of the organization that the committee is a part of>, 
    scope: <one of the following local, regional, national, international>}]
    }

     If a field is not explicitly present, set it to null.

    Text:
    {text}    
    """,

"intellectual_property": """
    Extract the following information from the chunk of text provided below. This is the intellectual property section of a CV and includes
    patents, copyrights, licenses, disclosures or trademarks. 

    For each item your reponse should be in the following json format:
    {intellectual:[{ date:<filing date>, 
    no:<patent/copyright/trademark/disclosure/license number>, 
    state:<state or province>, 
    country:<country>, 
    joint_holders:<| separated list of joint holder names if applicable>
    type:<one of the following, patent, trademark, copyright, disclosure, license}
    description: <if present description of the item>]
    }

     If a field is not explicitly present, set it to null.

    Text:
    {text}
    """,


"creative":"""
     Extract the following information from the chunk of text provided below. This is the creative professional activities section of a CV and includes
     professional innovations, contributions to the development of professional practices, and instances of examplary professional practice

     for each item your response should be in the following json format:

     {creative:[{
     start:<start date>, 
     end:<end date if applicable>, 
     title:<title of the innovation>, 
     description:<description of the innovation>, 
     impact:<impact of innovation>, 
     type:<either innovation, contribution, or examplary>]},

      If a field is not explicitly present, set it to null.

    Text:
    {text}
    """,

"media": """

    Extract the following information from the chunk of text provided below. This is the media section of a CV and includes
    interviews or features in news, radio, press, or other general-audience outlets.
    Exclude scientific or professional society communications and presentations.

    For each media item your response should be in the following json format:
    {media:[{
    date:<appearance date>, 
    role:<what kind of appearance>, 
    topic:<topic discussed or presented>, 
    program:<name of the broadcast program>, 
    network:<name of the network broadcasting>, 
    city:<city of appearance>, 
    state:<state or province of appearance>, 
    country:<country of appearance>, 
    scope:<geographic scope (local, regional, national, international)>, 
    }, ]} 

    Do not infer audience or intent. Use null when unspecified.

    Text:
    {text}
    """,

"profile": """
    Extract the following information from the chunk of text provided below. This section includes ONLY narrative
    personal statements describing philosophy, values, or vision related to research, teaching, or professional practice.

    Your response should be in the following json format:
    {profile:{
    research_statement:<full narrative text>}, 
    teaching_philosophy_summary:<full text of teaching phiolsophy and summary of activitites>, 
    creative:<full text of creative and professional activities statement>, other:<other sections go here>}

    If no narrative personal statement for a section is present, return null.

    Text:
    {text}
    """,

"rules": """

    Rules:
    - Do not invent or modify sections
    - Not every possible item will be in each section
    - There will usually be more than one item in each section find all of them individuall
    - always return json, no markdown, no comments, no additional formatting
    """
}
