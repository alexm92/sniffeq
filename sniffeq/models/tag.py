from mongoengine import *

from sniffeq.models.base import SEBaseModel


class Tag(SEBaseModel, Document):
    tag = StringField(max_length=256, unique_with='version')
    version = StringField(max_length=20)
    custom = BooleanField()
    abstract = BooleanField()
    datatype = StringField(max_length=20)
    iord = StringField(max_length=1)
    crdr = StringField(max_length=1)
    tlabel = StringField(max_length=512)
    doc = StringField(max_length=2048)

    meta = {'indexes': ['tag', 'version']}

