from mongoengine import *


class SEBaseModel(object):

    def __str__(self):
        return self.to_json()

