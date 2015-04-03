from mongoengine import *
from datetime import datetime

from sniffeq.models.base import SEBaseModel
from sniffeq.models.submission import Submission
from sniffeq.models.tag import Tag


class Number(SEBaseModel, Document):
    adsh = StringField(max_length=20, unique_with=['tag', 'version', 'ddate', 'qtrs', 'uom', 'coreg'])
    tag = StringField(max_length=256)
    version = StringField(max_length=20)
    ddate = DateTimeField()
    qtrs = IntField(default=0)
    uom = StringField(max_length=20)
    coreg = StringField(max_length=256, default='')
    value = FloatField(default=0)
    footnote = StringField(max_length=1024)

    tagRef = ReferenceField(Tag)
    submissionRef = ReferenceField(Submission)

    meta = {'indexes': ['adsh', 'tag', 'version']}

    def save(self, *args, **kwargs):
        if isinstance(self.ddate, str):
            self.ddate = datetime.strptime(self.ddate, '%Y%m%d')
        return super(Number, self).save(*args, **kwargs)

