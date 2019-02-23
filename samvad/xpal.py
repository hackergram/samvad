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
from copy import deepcopy

samvadxpal = Xetrapal(configfile="/opt/samvad-appdata/samvadxpal.conf")
baselogger = samvadxpal.logger
# Setting up mongoengine connections
samvadxpal.logger.info("Setting up MongoEngine")
mongoengine.connect('samvad', alias='default')
# samvadfb = samvadxpal.get_fb_browser()
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
    # if new is True:
    #    required_keys = ["vyakti_id"]
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
        required_keys = ["sandesh"]
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


def create_abhivyakti(abhivyaktidict, logger=baselogger):
    if validate_abhivyakti_dict(abhivyaktidict)['status']:
        try:
            abhivyakti = documents.AbhiVyakti(**abhivyaktidict)
            abhivyakti.save()
            logger.info("AbhiVyakti created {}".format(abhivyakti))
            return abhivyakti
        except Exception as e:
            logger.error("{} {}".format(type(e), str(e)))
            return "{} {}".format(type(e), str(e))


def create_abhivyakti_neo(logger=baselogger, **kwargs):
    if validate_abhivyakti_dict(kwargs)['status']:
        try:
            if "platform" in kwargs.keys():
                if kwargs['platform'] == "whatsapp":
                    abhivyakti = samvadgraphmodel.WhatsappAbhiVyakti(payload=kwargs, **kwargs).save()
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


def create_sandesh(sandeshdict, logger=baselogger):
    if validate_sandesh_dict(sandeshdict)['status']:
        try:
            sandesh = documents.Sandesh(**sandeshdict)
            sandesh.save()
            logger.info("{} created".format(sandesh))
            return sandesh
        except Exception as e:
            logger.error("{} {}".format(type(e), str(e)))
            return "{} {}".format(type(e), str(e))


def create_sandesh_neo(logger=baselogger, **sandeshdict):
    if validate_sandesh_dict(sandeshdict)['status']:
        try:
            sandesh = samvadgraphmodel.Sandesh(**sandeshdict).save()
            payload = {}
            for key in sandeshdict.keys():
                if type(sandeshdict[key]) != datetime.datetime:
                    payload[key] = sandeshdict[key]
            sandesh.payload = payload
            sandesh.save()
            logger.info("{} Node created".format(sandesh))
            return sandesh
        except Exception as e:
            logger.error("{} {}".format(type(e), str(e)))
            return "{} {}".format(type(e), str(e))


def search_sandesh(search_keys, logger=baselogger):
    date_frm = None
    date_to = None
    vyakti_id = None
    frm_abhivyakti = None
    samvad_id = None
    logger.info(search_keys)
    if "date_frm" in search_keys and search_keys['date_frm'] != "":
        date_frm = datetime.datetime.strptime(
            search_keys['date_frm'], "%Y-%m-%d %H:%M:%S")
    if "date_to" in search_keys and search_keys['date_to'] != "":
        date_to = datetime.datetime.strptime(
            search_keys['date_to'], "%Y-%m-%d %H:%M:%S")
    if "vyakti_id" in search_keys and search_keys['vyakti_id'] != "0":
        vyakti_id = search_keys['vyakti_id']
    if "frm_abhivyakti" in search_keys and search_keys['frm_abhivyakti'] != "0":
        frm_abhivyakti = search_keys['frm_abhivyakti']
    if "samvad_id" in search_keys and search_keys['samvad_id'] != "0":
            samvad_id = search_keys['samvad_id']
    if samvad_id is not None:
        logger.info("Getting sandeshes from samvad {}".format(samvad_id))
        # sandeshlist = documents.Sandesh.objects(id__in=[sandesh.id for sandesh in documents.Samvad.objects.with_id(samvad_id).sandesh])
        sandeshlist = documents.Sandesh.objects(samvads=samvad_id)
    else:
        logger.info("Getting all sandeshes")
        sandeshlist = documents.Sandesh.objects
    if vyakti_id is not None:
        logger.info("Filtering from vyakti from {}".format(vyakti_id))
        sandeshlist = sandeshlist.filter(vyakti_id=vyakti_id)
    if frm_abhivyakti is not None:
        logger.info("Filtering from abhivyakti {}".format(frm_abhivyakti))
        sandeshlist = sandeshlist.filter(frm=frm_abhivyakti)
    if date_frm is not None:
        logger.info("Filtering to date from {}".format(date_frm))
        sandeshlist = sandeshlist.filter(created_timestamp__gt=date_frm)
    if date_to is not None:
        logger.info("Filtering to date to {}".format(date_to))
        sandeshlist = sandeshlist.filter(created_timestamp__lt=date_to)
    return sandeshlist


def create_samvad(samvaddict, logger=baselogger):
    # Placeholder
    return samvaddict


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
    tabdata['friends']['count'] = int(fbbrowser.find_element_by_xpath("//a[@data-tab-key='friends']").get_property("text").replace("Friends", "").replace("Mutual", ""))
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


def wa_get_conv_messages(wabrowser, text, historical=True, logger=baselogger):
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
            if count == 2:
                break
        if newnumlines == numlines:
            break
        count += 1
    return lines


def wa_get_message(wabrowser, line, logger=baselogger):
    msgdict = {}
    try:
        wabrowser.execute_script("arguments[0].scrollIntoView(true)", line)
        linebs = BeautifulSoup(line.get_property("innerHTML"))
        message = linebs.find_all("div", {"class": "message-in"})
        # TODO: Replace with Whatsapp Classmap in Xetrapal
        if len(message):
            msg = linebs.find("div", {"class": "copyable-text"})
            if msg:
                msgts = msg.get("data-pre-plain-text").split("] ")[0].replace("[", "").replace("]", "")
                msgsender = msg.get("data-pre-plain-text").split("] ")[1]
                msgdict["created_timestamp"] = utils.get_utc_ts(datetime.datetime.strptime(msgts, "%H:%M %p, %m/%d/%Y"))
                if not utils.engalpha.search(msgsender):
                    msgdict['sender'] = msgsender.replace(": ", "").replace(" ", "")
                else:
                    msgdict['sender'] = msgsender.replace(": ", "")
                msgdict['content'] = [x for x in msg.strings]
                try:
                    msgdict['displayed_sender'] = linebs.find("span", {"class": "RZ7GO"}).text
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
            return msgdict
        else:
            return "No message in line"
    except Exception as e:
        return str(e)


def wa_update_samvad_sandesh(wabrowser, samvad, logger=baselogger):
    p = wa_get_conv_messages(wabrowser, samvad.naam, historical=False)
    messages = []
    for message in p:
        m = wa_get_message(wabrowser, message)
        if type(m) == dict and m != {}:
            messages.append(m)
    for message in messages:
        if len(documents.Sandesh.objects(sender=message['sender'], sandesh="\n".join(message['content']))) == 0:
            # Alter to use create_abhivyakti
            try:
                message['sandesh'] = "\n".join(message['content'])
                if validate_sandesh_dict(message)['status'] is True:
                    m = create_sandesh(message)
                    m.platform = "whatsapp"
                    m.samvads.append(str(samvad.id))
                    m.save()
                    logger.info("Created sandesh {}".format(m))
                    a = documents.AbhiVyakti(type=m.medium)
                    if utils.engalpha.search(m.sender):
                        logger.info("Found Whatsapp Contact: {}".format(m.sender))
                        a = documents.AbhiVyakti.objects(type="whatsapp", whatsapp_contact=m.sender)
                        if len(a) == 0:
                            ab = documents.AbhiVyakti(type="whatsapp")
                            ab.whatsapp_contact = m.sender
                            ab.save()
                            logger.info("Created Abhivyakti {}".format(ab))
                            m.frm = ab
                            m.save()
                        else:
                            logger.info("AbhiVyakti Exists")
                            m.frm = a[0]
                            m.save()

                    else:
                        logger.info("Found Mobile Num: {}".format(m.sender))
                        a = documents.AbhiVyakti.objects(type="whatsapp", mobile_num=m.sender)
                        if len(a) == 0:
                            ab = documents.AbhiVyakti(type="whatsapp")
                            ab.mobile_num = m.sender
                            ab.save()
                            logger.info("Created Abhivyakti {}".format(ab))
                            m.frm = ab
                            m.save()
                        else:
                            logger.info("AbhiVyakti Exists")
                            m.frm = a[0]
                            m.save()
                    samvad.sandesh.append(m)
                    samvad.save()
                    logger.info("Added sandesh {} to samvad {}".format(m, samvad))
                else:
                    logger.error(validate_sandesh_dict(message)['message'])
            except Exception as e:
                logger.error("{} {}".format(type(e), str(e)))
        else:
            logger.error("{} is a duplicate of a previous sandesh".format(message))


def create_sandesh_graph(logger=baselogger):
    for sandesh in documents.Sandesh.objects:
        sandeshdict = json.loads(sandesh.dump_dict())
        samvadlist = []
        for samvad in sandeshdict['samvads']:
            samvadlist.append(documents.Samvad.objects.with_id(samvad).naam)
        sandeshdict['samvads'] = samvadlist
        sandeshdict['created_timestamp'] = datetime.datetime.strptime(sandeshdict['created_timestamp'], "%Y-%m-%d %H:%M:%S")
        sandeshdict['updated_timestamp'] = datetime.datetime.strptime(sandeshdict['updated_timestamp'], "%Y-%m-%d %H:%M:%S")
        print(sandeshdict.keys())
        newsandesh = create_sandesh_neo(**sandeshdict)
        searchdict = {}
        searchdict['platform'] = newsandesh.platform
        if utils.engalpha.search(newsandesh.sender):
            logger.info("Whatsapp Contact: {}".format(sandesh.sender))
            searchdict['whatsapp_contact'] = sandesh.sender
        else:
            logger.info("Mobile Num: {}".format(sandesh.sender))
            searchdict['mobile_num'] = sandesh.sender
        if searchdict == {}:
            return sandesh
        try:
            abhivyakti = search_abhivyakti(**searchdict)
            if len(abhivyakti) > 0:
                logger.info("Found abhivyakti, linking")
                newsandesh.frm.connect(abhivyakti[0])
            else:
                logger.info("Creating abhivyakti, linking")
                newabhivyakti = create_abhivyakti_neo(**searchdict)
                # newabhivyakti = samvadgraphmodel.AbhiVyakti(**searchdict).save()
                newsandesh.frm.connect(newabhivyakti)
            newsandesh.save()
        except Exception as e:
            logger.error("Error {} {} trying to create AbhiVyakti".format(type(e), str(e)))
