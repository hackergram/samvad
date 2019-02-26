# -*- coding: utf-8 -*-
"""
Created on 2019-01-09

@author: arjunvenkatraman
"""
from neomodel import (config, JSONProperty, StructuredNode, StringProperty, ArrayProperty, RelationshipTo, RelationshipFrom, DateTimeProperty, db)

# from mongoengine import Document, fields, DynamicDocument
import datetime
# from flask_mongoengine import QuerySet
# from samvad import utils
# import json


class SamvadBase(StructuredNode):
    created_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    updated_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    payload = JSONProperty(default={})
    platform = StringProperty(default="samvad")


class AbhiVyakti(SamvadBase):
    vyakti = RelationshipFrom("Vyakti", "USES")
    lastseen_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    sent = RelationshipTo("Sandesh", "SENT")
    lastinteracted_timestamp = DateTimeProperty()
    naam = ArrayProperty(default=[])
    platform = StringProperty(default="abhivyakti")


class WhatsappAbhiVyakti(AbhiVyakti):
    mobile_num = StringProperty()
    whatsapp_contact = StringProperty()
    platform = StringProperty(default="whatsapp")


class Vyakti(SamvadBase):
    vyakti_id = StringProperty(unique=True)
    lastseen_timestamp = DateTimeProperty(default=datetime.datetime.utcnow)
    lastinteracted_timestamp = DateTimeProperty()
    naam = ArrayProperty()
    abhivyakti = RelationshipTo("AbhiVyakti", "USES")
    platform = StringProperty(default="whatsapp")

    def __str__(self):
        return "Vyakti (%r)" % (self.vyakti_id)


class Sandesh(SamvadBase):
    text = StringProperty()
    sender = JSONProperty()
    frm = RelationshipFrom("AbhiVyakti", "SENT")
    samvads = RelationshipFrom("Samvad", "CONTAINS")
    platform = StringProperty(default="sandesh")

    def fill(self):
        if "text_lines" in self.payload.keys():
            self.sandesh = "\n".join(self.payload['text_lines'])
        self.save()


class Samvad(SamvadBase):
    platform = StringProperty(default="samvad")
    sandesh = RelationshipTo("Sandesh", "CONTAINS")
    naam = StringProperty()
