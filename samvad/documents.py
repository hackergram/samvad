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
                    name, value.strftime("%Y-%m-%d %H:%M:%S")))
            else:
                attrs.append('\n    {} = {!r},'.format(name, value))
        if self._dynamic_fields:
            for name in self._dynamic_fields.keys():
                value = getattr(self, name)
                if isinstance(value, (Document, DynamicDocument)):
                    attrs.append('\n    {} = {!s},'.format(name, value))
                elif isinstance(value, (datetime.datetime)):
                    attrs.append('\n    {} = {},'.format(
                        name, value.strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    attrs.append('\n    {} = {!r},'.format(name, value))
        return '\n{}: {}\n'.format(type(self).__name__, ''.join(attrs))


class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))


class Vyakti(PPrintMixin, DynamicDocument):
    vyakti_id = fields.StringField(unique=True, required=True)
    created_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    updated_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    lastseen_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    lastinteracted_timestamp = fields.DateTimeField()
    naam = fields.ListField()

    def __str__(self):
        return "Vyakti (%r)" % (self.vyakti_id)


class AbhiVyakti(PPrintMixin, DynamicDocument):
    vyakti = fields.ReferenceField(Vyakti)
    created_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    updated_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    lastseen_timestamp = fields.DateTimeField(default=datetime.datetime.utcnow(), required=True)
    lastinteracted_timestamp = fields.DateTimeField()
    naam = fields.ListField()
    flavor = fields.StringField(default="abhivyakti")
