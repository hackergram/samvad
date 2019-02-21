# -*- coding: utf-8 -*-
"""
Created on 2019-01-09

@author: arjunvenkatraman
"""
from neomodel import (config, StructuredNode, StringProperty, ArrayProperty, IntegerProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom, DateTimeProperty)

# from mongoengine import Document, fields, DynamicDocument
import datetime
# from flask_mongoengine import QuerySet
# from samvad import utils
# import json
import bson

'''
class PPrintMixin(object):
    def __str__(self):
        return '<{}: id={!r}>'.format(type(self).__name__, self.id)

    def __repr__(self):
        attrs = []
        for name in self._fields.keys():
            value = getattr(self, name)
            if isinstance(value, (Document, DynamicDocument)):
                attrs.append('\n    {} = {!s},'.format(name, value))
            elif isinstance(value, (datetime.datetime)):
                attrs.append('\n    {} = {},'.format(
                    name, utils.get_local_ts(value).strftime("%Y-%m-%d %H:%M:%S")))
            else:
                attrs.append('\n    {} = {!r},'.format(name, value))
        if self._dynamic_fields:
            for name in self._dynamic_fields.keys():
                value = getattr(self, name)
                if isinstance(value, (Document, DynamicDocument)):
                    attrs.append('\n    {} = {!s},'.format(name, value))
                elif isinstance(value, (datetime.datetime)):
                    attrs.append('\n    {} = {},'.format(
                        name, utils.get_local_ts(value).strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    attrs.append('\n    {} = {!r},'.format(name, value))
        return '\n{}: {}\n'.format(type(self).__name__, ''.join(attrs))


class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))

'''


class SamvadBase(StructuredNode):
    created_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    updated_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)


class AbhiVyakti(SamvadBase):
    vyakti = RelationshipFrom("Vyakti", "USES")
    lastseen_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    sent = RelationshipTo("Sandesh", "SENT")
    lastinteracted_timestamp = DateTimeProperty()
    naam = ArrayProperty()
    type = StringProperty(default="abhivyakti")
    mobile_num = StringProperty()


class Vyakti(SamvadBase):
    vyakti_id = StringProperty(unique=True)
    lastseen_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    lastinteracted_timestamp = DateTimeProperty()
    naam = ArrayProperty()
    abhivyakti = RelationshipTo("AbhiVyakti", "USES")

    def __str__(self):
        return "Vyakti (%r)" % (self.vyakti_id)


class Sandesh(SamvadBase):
    sandesh = StringProperty()
    sender = StringProperty()
    frm = RelationshipFrom("AbhiVyakti", "SENT")
    samvads = RelationshipFrom("Samvad", "CONTAINS")


class Samvad(SamvadBase):
    sandesh = RelationshipTo("Sandesh", "CONTAINS")
    naam = StringProperty()
