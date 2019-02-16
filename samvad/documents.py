#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on 2019-01-09

@author: arjunvenkatraman
"""

from mongoengine import Document, fields, DynamicDocument
import datetime
from flask_mongoengine import QuerySet
from samvad import utils
import json
import bson


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


class SamvadBase(PPrintMixin):
    created_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow, required=True)
    updated_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow, required=True)


class AbhiVyakti(SamvadBase, DynamicDocument):
    owner = fields.StringField()
    lastseen_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    vyaktis = fields.ListField()
    lastinteracted_timestamp = fields.DateTimeField()
    naam = fields.ListField()
    type = fields.StringField(default="abhivyakti")


class Vyakti(SamvadBase, DynamicDocument):
    vyakti_id = fields.StringField(unique=True)
    lastseen_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    lastinteracted_timestamp = fields.DateTimeField()
    naam = fields.ListField()
    abhivyaktis = fields.ListField(fields.ReferenceField(AbhiVyakti))

    def __str__(self):
        return "Vyakti (%r)" % (self.vyakti_id)


class Sandesh(SamvadBase, DynamicDocument):
    sandesh = fields.StringField()
    sender = fields.StringField()
    frm = fields.ReferenceField(AbhiVyakti)


class Samvad(SamvadBase, DynamicDocument):
    sandesh = fields.SortedListField(fields.ReferenceField(Sandesh))
    naam = fields.StringField()
    meta = {'queryset_class': CustomQuerySet}

    def to_json(self):
        data = {}
        data['sandeshcount'] = len(self.sandesh)
        data['naam'] = self.naam
        data['_id'] = self.id
        # data['sandesh'] = [json.loads(sandesh.to_json()) for sandesh in self.sandesh]
        return bson.json_util.dumps(data)

    def dump_sandesh(self):
        data = self.to_mongo()
        data['sandeshcount'] = len(self.sandesh)
        data['sandesh'] = [json.loads(sandesh.to_json()) for sandesh in self.sandesh]
        return bson.json_util.dumps(data['sandesh'])
