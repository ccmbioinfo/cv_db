import os

from cv_db.parser.prompts import *
from cv_db.parser.models import *

from cv_db.parser.parser import *
from cv_db.parser.classifier import *
from cv_db.parser.extractor import *

#TODO need to think about this
@dataclass
class CV:
    filename: str
    sections: list
    section_classes: list[SectionClassification]

class Pipeline:
    def __init__(self, parser:CVParser, classifier:SectionClassifier, extractor:SectionExtractor):
        self.parser = parser
        self.classifier = classifier
        self.extractor = extractor

    def __call__(self, file):
        if not os.path.isfile(file):
            raise ValueError(f"File {file} does not exist or is not a file.")

        sections=self.parser(file)
        classification=self.classifier(sections)
        #TODO this needs to be it's own dataclaass
        extracted_info={}
        for section, section_class in zip(sections, classification):
            pass


