from mongoengine import *

from sniffeq.models.base import SEBaseModel
from sniffeq.models.submission import Submission
from sniffeq.models.number import Number
from sniffeq.models.tag import Tag


STMT_CHOICES = (
    ('BS', 'Balance Sheet'), 
    ('IS', 'Income Statement'), 
    ('CF', 'Cash Flow'), 
    ('EQ', 'Equity'), 
    ('CI', 'Comprehensive Income'), 
    ('UN', 'Unclassifiable Statement'),
)

class Presentation(SEBaseModel, Document):
    adsh = StringField(max_length=20, unique_with=['report', 'line'])
    report = IntField()
    line = IntField()
    stmt = StringField(max_length=2, choices=STMT_CHOICES)
    inpth = BooleanField()
    rfile = StringField(max_length=1)
    tag = StringField(max_length=256)
    version = StringField(max_length=20)
    plabel = StringField(max_length=1024)

    submissionRef = ReferenceField(Submission)
    tagRef = ReferenceField(Tag)
    numbersRef = ListField(ReferenceField(Number))

    meta = {'indexes': ['adsh']}

