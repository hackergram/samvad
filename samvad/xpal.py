"""
Created on Sat Jan  12 21:52:07 2019

@author: arjunvenkatraman
"""
import os
import mongoengine
import json
from xetrapal import Xetrapal, whatsappkarmas, karma
from samvad import documents, utils, samvadgraphmodel
import datetime
from bs4 import BeautifulSoup


class TZ(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(minutes=0)


samvadxpal = Xetrapal(configfile="/opt/samvad-appdata/samvadxpal.conf")
baselogger = samvadxpal.logger
# Setting up mongoengine connections
samvadxpal.logger.info("Setting up MongoEngine")
mongoengine.connect('samvad', alias='default')
samvadgraphmodel.config.DATABASE_URL = 'bolt://neo4j:test123@localhost:7687'


def validate_vyakti_dict(vyaktidict, new=True, logger=baselogger):
    validation = {}
    validation['status'] = True
    validation['message'] = "Valid vyakti"
    required_keys = []
    if new is True:
        required_keys = ["vyakti_id"]
    string_keys = ["first_name", "last_name",
                   "mobile_num", "name", "vyakti_id"]
    mobile_nums = ["mobile_num"]
    validation = utils.validate_dict(
        vyaktidict, required_keys=required_keys, string_keys=string_keys, mobile_nums=mobile_nums)
    if validation['status'] is True:
        logger.info("vyaktidict: " + validation['message'])
    else:
        logger.error("vyaktidict: " + validation['message'])
    return validation


def validate_abhivyakti_dict(vyaktidict, new=True, logger=baselogger):
    validation = {}
    validation['status'] = True
    validation['message'] = "Valid abhivyakti"
    required_keys = []
    string_keys = ["mobile_num"]
    mobile_nums = ["mobile_num"]
    validation = utils.validate_dict(
        vyaktidict, required_keys=required_keys, string_keys=string_keys, mobile_nums=mobile_nums)
    if validation['status'] is True:
        logger.info("abhivyaktidict: " + validation['message'])
    else:
        logger.error("abhivyaktidict: " + validation['message'])
    return validation


def validate_sandesh_dict(sandeshdict, new=True, logger=baselogger):
    validation = {}
    validation['status'] = True
    validation['message'] = "Valid abhivyakti"
    required_keys = []
    if new is True:
        required_keys = []
    string_keys = []
    mobile_nums = []
    validation = utils.validate_dict(
        sandeshdict, required_keys=required_keys, string_keys=string_keys, mobile_nums=mobile_nums)
    if validation['status'] is True:
        logger.info("sandeshdict: " + validation['message'])
    else:
        logger.error("sandeshdict: " + validation['message'])
    return validation


def create_vyakti(vyaktidict, logger=baselogger):
    if validate_vyakti_dict(vyaktidict)['status']:
        try:
            vyakti = documents.Vyakti(**vyaktidict)
            vyakti.save()
            logger.info("{} created".format(vyakti))
            return vyakti
        except Exception as e:
            logger.error("{} {}".format(type(e), str(e)))
            return "{} {}".format(type(e), str(e))
    else:
        errmsg = validate_vyakti_dict(vyaktidict, new=False)['message']
        logger.error("{}".format(errmsg))
        return "error:" + errmsg


def update_vyakti(vyakti_id, vyaktidict, logger=baselogger):
    vyakti = documents.Vyakti.objects(vyakti_id=vyakti_id)
    if "vyakti_id" in vyaktidict.keys():
        vyaktidict.pop("vyakti_id")
    if len(vyakti):
        vyakti = vyakti[0]
        if validate_vyakti_dict(vyaktidict, new=False)['status']:
            try:
                logger.info("Trying to save {} to {}".format(vyaktidict, vyakti))
                vyakti.update(**vyaktidict)
                vyakti.save()
                vyakti.reload()
                return vyakti
            except Exception as e:
                logger.error("{} {}".format(type(e), str(e)))
                return "error: {} {}".format(type(e), str(e))
        else:
            errmsg = validate_vyakti_dict(vyaktidict, new=False)['message']
            logger.error("{}".format(errmsg))
            return "error:" + errmsg
    else:
        logger.error("No vyakti by id {}".format(vyakti_id))
        return "error: No vyakti by id {}".format(vyakti_id)


def delete_vyakti(vyakti_id, logger=baselogger):
    d = documents.Vyakti.objects(vyakti_id=vyakti_id)
    if len(d):
        d[0].delete()
        return []
    else:
        return "error: No Vyakti by that id"


def sighted_vyakti(vyakti, logger=baselogger):
    vyakti.lastseen_timestamp = datetime.datetime.utcnow()
    vyakti.save()
    logger.info("{} sighted at {}".format(vyakti, utils.get_local_ts(vyakti.lastseen_timestamp).strftime("%Y-%m-%d %H:%M:%S")))


def create_abhivyakti(logger=baselogger, **kwargs):
    if validate_abhivyakti_dict(kwargs)['status']:
        try:
            if "platform" in kwargs.keys():
                if kwargs['platform'] == "whatsapp":
                    abhivyakti = samvadgraphmodel.WhatsappAbhiVyakti(payload=kwargs, **kwargs).save()
                    if hasattr(abhivyakti, "mobile_num"):
                        if abhivyakti.mobile_num is not None:
                            logger.info("Updating naam with {}".format(abhivyakti.mobile_num))
                            abhivyakti.naam.append(abhivyakti.mobile_num)
                    if hasattr(abhivyakti, "whatsapp_contact"):
                        if abhivyakti.whatsapp_contact is not None:
                            logger.info("Updating naam with {}".format(abhivyakti.whatsapp_contact))
                            abhivyakti.naam.append(abhivyakti.whatsapp_contact)
                    abhivyakti.save()
            else:
                abhivyakti = samvadgraphmodel.AbhiVyakti(payload=kwargs, **kwargs).save()
            logger.info("AbhiVyakti created {}".format(abhivyakti))
            return abhivyakti
        except Exception as e:
            logger.error("{} {}".format(type(e), str(e)))
            return "{} {}".format(type(e), str(e))


def search_abhivyakti(logger=baselogger, **kwargs):
    platformclass = "AbhiVyakti"
    if "platform" in kwargs.keys():
        if kwargs['platform'] == "whatsapp":
            platformclass = "WhatsappAbhiVyakti"
    query = "MATCH (p:{}) ".format(platformclass)
    if kwargs != {}:
        for key, value in kwargs.items():
            if "WHERE" in query:
                if key == "naam":
                    query += " AND '{}' IN p.{}".format(value, key)
                else:
                    query += " AND p.{} = '{}'".format(key, value)
            else:
                if key == "naam":
                    query += "WHERE '{}' IN p.{}".format(value, key)
                else:
                    query += "WHERE p.{}='{}'".format(key, value)
    query += " RETURN p"
    logger.info("Running AbhiVyakti Search with query "+query)
    try:
        results, meta = samvadgraphmodel.db.cypher_query(query)
        if "platform" in kwargs.keys():
            if kwargs['platform'] == "whatsapp":
                return [samvadgraphmodel.WhatsappAbhiVyakti.inflate(row[0]) for row in results]
        return [samvadgraphmodel.AbhiVyakti.inflate(row[0]) for row in results]
    except Exception as e:
        logger.error("Error {} {} running query".format(type(e), str(e)))
        return []


def delete_abhivyakti(abhivyakti_id, logger=baselogger):
    d = [documents.AbhiVyakti.objects.with_id(abhivyakti_id)]
    if len(d):
        d[0].delete()
        return []
    else:
        return "error: No AbhiVyakti by that id"


def update_abhivyakti(abhivyakti_id, abhivyaktidict, logger=baselogger):
    abhivyakti = documents.Vyakti.objects.with_id(abhivyakti_id)
    if "abhivyakti_id" in abhivyaktidict.keys():
        abhivyaktidict.pop(abhivyakti_id)
    if len(abhivyakti):
        abhivyakti = abhivyakti[0]
        if validate_abhivyakti_dict(abhivyaktidict, new=False)['status']:
            try:
                abhivyakti.update(**abhivyaktidict)
                abhivyakti.save()
                abhivyakti.reload()
                return abhivyakti
            except Exception as e:
                logger.error("{} {}".format(type(e), str(e)))
                return "error: {} {}".format(type(e), str(e))
        else:
            errmsg = validate_abhivyakti_dict(abhivyaktidict, new=False)['message']
            logger.error("{}".format(errmsg))
            return "error:" + errmsg
    else:
        logger.error("No vyakti by id {}".format(abhivyakti_id))
        return "error: No vyakti by id {}".format(abhivyakti_id)


def create_sandesh(logger=baselogger, **sandeshdict):
    if validate_sandesh_dict(sandeshdict)['status']:
        if "sender" in sandeshdict.keys():
            abhivyakti = search_abhivyakti(**sandeshdict['sender'])
        if len(abhivyakti) == 0:
            abhivyakti = create_abhivyakti(**sandeshdict['sender']).save()
        else:
            abhivyakti = abhivyakti[0]
        sandesh = search_sandesh(**sandeshdict)
        if sandesh == []:
            try:
                sandesh = samvadgraphmodel.Sandesh(**sandeshdict).save()
                payload = {}
                for key in sandeshdict.keys():
                    if type(sandeshdict[key]) != datetime.datetime:
                        payload[key] = sandeshdict[key]
                sandesh.payload = payload
                if "text_lines" in sandeshdict.keys():
                    sandesh.text = "\n".join(sandeshdict['text_lines'])
                    sandesh.text = sandesh.text.replace("'", "")
                sandesh.frm.connect(abhivyakti)
                sandesh.save()
                logger.info("{} Node created".format(sandesh))
                return sandesh
            except Exception as e:
                logger.error("{} {}".format(type(e), str(e)))
                return "{} {}".format(type(e), str(e))
        else:
            logger.error("Duplicate message of {}".format(sandesh[0]))
            return sandesh[0]


def search_sandesh(logger=baselogger, **kwargs):
    platformclass = "Sandesh"
    searchkeys = {}
    for key in kwargs.keys():
        if type(kwargs[key]) == str:
            searchkeys[key] = "'{}'".format(kwargs[key].replace("'", ""))
        if type(kwargs[key]) == datetime.datetime:
            searchkeys[key] = "{}".format(kwargs[key].replace(tzinfo=TZ()).timestamp())
        if key == "text_lines":
            searchkeys['text'] = "'{}'".format("\n".join(kwargs['text_lines']).replace("'", ""))
    query1 = "MATCH (p:{}) ".format(platformclass)
    if searchkeys != {}:
        for key, value in searchkeys.items():
            if "WHERE" in query1:
                query1 += " AND p.{} = {}".format(key, value)
            else:
                query1 += "WHERE p.{}={}".format(key, value)
    if "sender" in kwargs.keys():
        sender = kwargs['sender']
        platformclass2 = "AbhiVyakti"
        if "platform" in sender.keys():
            if kwargs['platform'] == "whatsapp":
                platformclass2 = "WhatsappAbhiVyakti"
        searchkeys2 = {}
        for key in sender.keys():
            if type(sender[key]) == str:
                searchkeys2[key] = "'{}'".format(sender[key].replace("'", ""))
        query2 = " MATCH (b:{}) ".format(platformclass2)
        for key, value in searchkeys2.items():
            if "WHERE" in query2:
                query2 += " AND b.{} = {}".format(key, value)
            else:
                query2 += "WHERE b.{}={}".format(key, value)
        query2 += " AND (b)-[:SENT]->(p)"
        query1 += query2
    query1 += " RETURN p"
    logger.info("Running Sandesh Search with query "+query1)
    try:
        results, meta = samvadgraphmodel.db.cypher_query(query1)
        # if "platform" in kwargs.keys():
        #    if kwargs['platform'] == "whatsapp":
        #        return [samvadgraphmodel.WhatsappAbhiVyakti.inflate(row[0]) for row in results]
        # return [samvadgraphmodel.AbhiVyakti.inflate(row[0]) for row in results]
        return [samvadgraphmodel.Sandesh.inflate(row[0]) for row in results]
    except Exception as e:
        logger.error("Error {} {} running query".format(type(e), str(e)))
        return []


def sighted_abhivyakti(abhivyakti, logger=baselogger):
    abhivyakti.lastseen_timestamp = datetime.datetime.utcnow()
    abhivyakti.save()
    logger.info("{} sighted at {}".format(abhivyakti, abhivyakti.lastseen_timestamp.strftime("%Y-%m-%d %H:%M:%S")))


def fb_get_profile_data(fbbrowser, url, logger=baselogger):
    profiledata = {}
    profilepic = {}
    fbbrowser.get(url)
    karma.wait()
    profile = fbbrowser.current_url
    if profile == "http://www.facebook.com/profile.php":
        plink = fbbrowser.find_element_by_xpath("//a[@title='Profile']")
        profile = plink.get_attribute("href")
    profiledata['url'] = profile
    profiledata['fbdisplayname'] = fb_get_cur_page_displayname(fbbrowser)
    fbbrowser.find_element_by_class_name("profilePicThumb").click()
    karma.wait()
    try:
        profilepic['alttext'] = fbbrowser.find_element_by_class_name(
            "spotlight").get_property("alt")
        profilepic['src'] = fbbrowser.find_element_by_class_name(
            "spotlight").get_property("src")
        profilepic['profileguard'] = False
    except Exception as e:
        logger.error("{} {}".format(type(e), str(e)))
        profilepic['alttext'] = fbbrowser.find_element_by_class_name(
            "profilePic").get_property("alt")
        profilepic['src'] = fbbrowser.find_element_by_class_name(
            "profilePic").get_property("src")
        profilepic['profileguard'] = True
    try:
        localfile = karma.download_file(
            profilepic['src'], prefix=profiledata['fbdisplayname'].replace(" ", ""), suffix=".jpg")
        profilepic['localfile'] = localfile
    except Exception as e:
        logger.error("Failed to download {} {}".format(type(e), str(e)))
    profiledata['tabdata'] = fb_get_profile_tab_data(fbbrowser, url)
    profiledata['friendcount'] = profiledata['tabdata']['friends']['count']
    profiledata['profilepic'] = profilepic
    return profiledata


def fb_get_profile_tab_data(fbbrowser, profileurl, logger=baselogger):
    tabdata = {"friends": {}, "photos": {}, "about": {}}
    fbbrowser.get(profileurl)
    karma.wait()
    phototab = fbbrowser.find_element_by_xpath(
        "//a[@data-tab-key='photos']").get_property("href")
    friendtab = fbbrowser.find_element_by_xpath(
        "//a[@data-tab-key='friends']").get_property("href")
    abouttab = fbbrowser.find_element_by_xpath(
        "//a[@data-tab-key='about']").get_property("href")
    tabdata['friends']['url'] = friendtab
    # if fbbrowser.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text").replace("Friends", "") != "" and "Mutual" not in fbbrowser.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text"):
    try:
        tabdata['friends']['count'] = int(fbbrowser.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text").replace("Friends", "").replace("Mutual", ""))
    except Exception as e:
        logger.error("{} {}".format(type(e), str(e)))
        tabdata['friends']['count'] = 0
    # else:
    #    tabdata['friends']['count'] = -1
    tabdata['photos']['url'] = phototab
    tabdata['about']['url'] = abouttab
    return tabdata


def fb_get_cur_page_displayname(fbbrowser, logger=baselogger):
    displayname = fbbrowser.find_element_by_id("fb-timeline-cover-name").find_element_by_tag_name("a").text
    return displayname


def fb_like_page_toggle(fbbrowser, pageurl, logger=baselogger):
    fbbrowser.get(pageurl)
    likebutton = fbbrowser.find_element_by_xpath("//button[@data-testid='page_profile_like_button_test_id']")
    likebutton.click()


def wa_get_conv_messages(wabrowser, text, historical=True, scrolls=2, logger=baselogger):
    lines = []
    whatsappkarmas.select_conv(wabrowser, text)
    karma.wait()
    pane2 = wabrowser.find_element_by_class_name("_2nmDZ")
    count = 0
    while True:
        numlines = len(lines)
        wabrowser.execute_script("arguments[0].scrollTo(0,0)", pane2)
        lines = wabrowser.find_elements_by_class_name("vW7d1")
        # TODO: Replace with Whatsapp Classmap in Xetrapal
        karma.wait(waittime="long")
        newnumlines = len(lines)
        if historical is not True:
            if count == scrolls:
                break
        if newnumlines == numlines:
            break
        count += 1
    return lines


def wa_get_message(wabrowser, line, logger=baselogger):
    msgdict = {}
    try:
        wabrowser.execute_script("arguments[0].scrollIntoView(true)", line)
        linebs = BeautifulSoup(line.get_property("innerHTML"), features="html.parser")
        message = linebs.find_all("div", {"class": "message-in"})
        # TODO: Replace with Whatsapp Classmap in Xetrapal
        if len(message):
            msg = linebs.find("div", {"class": "copyable-text"})
            logger.info(msg)
            if msg:
                msgts = msg.get("data-pre-plain-text").split("] ")[0].replace("[", "").replace("]", "")
                msgsender = msg.get("data-pre-plain-text").split("] ")[1]
                msgdict["created_timestamp"] = utils.get_utc_ts(datetime.datetime.strptime(msgts, "%H:%M %p, %m/%d/%Y"))
                msgdict['sender'] = {"platform": "whatsapp"}
                if not utils.engalpha.search(msgsender):
                    msgdict['sender']['mobile_num'] = msgsender.replace(": ", "")
                    logger.info("Mobile Num: {}".format(msgdict['sender']))
                else:
                    msgdict['sender']['whatsapp_contact'] = msgsender.replace(": ", "")
                    logger.info("Whatsapp Contact: {}".format(msgdict['sender']))
                msgdict['text_lines'] = [x.replace("'", "") for x in msg.strings]
                try:
                    msgdict['sender']['displayed_sender'] = linebs.find("span", {"class": "RZ7GO"}).text
                    msgdict['displayed_sender_name'] = linebs.find("span", {"class": "_3Ye_R"}).text
                except Exception as e:
                    logger.error("Could not get display name and sender")
                images = message[0].find_all("img")
                if len(images):
                    image = line.find_element_by_tag_name("img")
                    if "blob" in image.get_attribute("src"):
                        image.click()
                        karma.wait()
                        files = os.listdir(samvadxpal.sessiondownloadpath)
                        wabrowser.find_element_by_xpath("//div[@title='Download']").click()
                        karma.wait(waittime="long")
                        newfiles = os.listdir(samvadxpal.sessiondownloadpath)
                        logger.info("Downloaded file {}".format(list(set(newfiles)-set(files))[0]))
                        msgdict['file'] = os.path.join(samvadxpal.sessiondownloadpath, list(set(newfiles)-set(files))[0])
                        karma.wait()
                        wabrowser.find_element_by_xpath("//div[@title='Close']").click()
                        karma.wait()
            if msgdict != {}:
                msgdict['platform'] = "whatsapp"
                logger.info(msgdict)
                return msgdict
        else:
            return "No message in line"
    except Exception as e:
        logger.error("{} {}".format(type(e), str(e)))
        return "{} {}".format(type(e), str(e))


def wa_update_samvad_sandesh(wabrowser, text, historical=False, logger=baselogger):
    p = wa_get_conv_messages(wabrowser, text, historical=historical)
    messages = []
    seen_messages = []
    # return messages
    for message in p:
        m = wa_get_message(wabrowser, message)
        if type(m) == dict and m != {}:
            messages.append(m)
    for sandesh in messages:
        q = create_sandesh(**sandesh)
        seen_messages.append(q)
    return seen_messages

def create_samvad(logger=baselogger, **samvadict):


def create_sandesh_graph(logger=baselogger):
    for sandesh in documents.Sandesh.objects:
        sandeshdict = json.loads(sandesh.dump_dict())
        create_sandesh(sandeshdict)
