import logging
from datetime import datetime
from mongoengine import *

from sniffeq.models.base import SEBaseModel


AFS_CHOICES = (
    ('1-LAF', 'Large Accelerated'),
    ('2-ACC', 'Accelerated'),
    ('3-SRA', 'Smaller Reporting Accelerated'),
    ('4-NON', 'Non-Accelerated'),
    ('5-SML', 'Smaller Reporting Filer'),
)
FP_CHOICES = ('?', 'FY', 'Q1', 'Q2', 'Q3', 'Q4', 'H1', 'H2', 'M9', 'T1', 'T2', 'T3', 'M8', 'CY')
log = logging.getLogger('models.submission')

class Submission(SEBaseModel, Document):
    adsh = StringField(max_length=20, unique=True) #_with=['year', 'quarter'])
    # year = IntField()
    # quarter = IntField()
    cik = IntField()
    name = StringField(max_length=150)
    sic = IntField()
    countryba = StringField(max_length=2)
    stprba = StringField(max_length=2)
    cityba = StringField(max_length=30)
    zipba = StringField(max_length=10)
    bas1 = StringField(max_length=40)
    bas2 = StringField(max_length=40)
    baph = StringField(max_length=12)
    countryma = StringField(max_length=2)
    stprma = StringField(max_length=2)
    cityma = StringField(max_length=30)
    zipma = StringField(max_length=10)
    mas1 = StringField(max_length=40)
    mas2 = StringField(max_length=40)
    countryinc = StringField(max_length=3)
    stprinc = StringField(max_length=2)
    ein = IntField()
    former = StringField(max_length=150)
    changed = StringField(max_length=8)
    afs = StringField(choices=AFS_CHOICES)
    wksi = BooleanField()
    fye = StringField(max_length=4)
    form = StringField(max_length=10)
    period = DateTimeField()
    fy = IntField()
    fp = StringField(max_length=2, choices=FP_CHOICES)
    filed = DateTimeField()
    accepted = DateTimeField()
    prevrpt = BooleanField()
    detail = BooleanField()
    instance = StringField(max_length=32)
    nciks = IntField()
    aciks = StringField(max_length=120)

    meta = {'indexes': ['adsh']}

    def save(self, *args, **kwargs):
	if not self.fy:
	    self.fy = None
	if not self.fp:
	    self.fp = None
	if not self.afs:
	   self.afs = None
        if isinstance(self.period, str):
            self.period = datetime.strptime(self.period, '%Y%m%d')
        if isinstance(self.filed, str):
            self.filed = datetime.strptime(self.filed, '%Y%m%d')

        return super(Submission, self).save(*args, **kwargs)

    @property
    def url(self):
        """
        Get sec.gov url for current form
        """
        url = 'http://www.sec.gov/Archives/edgar/data/{0}/{1}/{2}'
        return url.format(
            self.cik, 
            self.adsh.replace('-', ''),
            self.instance,
        )


