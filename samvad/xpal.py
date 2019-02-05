"""
Created on Sat Jan  12 21:52:07 2019

@author: arjunvenkatraman
"""

import mongoengine
import xetrapal
from samvad import documents, utils
import datetime

samvadxpal = xetrapal.Xetrapal(configfile="/opt/samvad-appdata/samvadxpal.conf")
baselogger = samvadxpal.logger
# Setting up mongoengine connections
samvadxpal.logger.info("Setting up MongoEngine")
mongoengine.connect('samvad', alias='default')
# samvadfb = samvadxpal.get_fb_browser()


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
    if new is True:
        required_keys = ["vyakti_id"]
    string_keys = ["mobile_num"]
    mobile_nums = ["mobile_num"]
    validation = utils.validate_dict(
        vyaktidict, required_keys=required_keys, string_keys=string_keys, mobile_nums=mobile_nums)
    if validation['status'] is True:
        logger.info("abhivyaktidict: " + validation['message'])
    else:
        logger.error("abhivyaktidict: " + validation['message'])
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


def sighted_vyakti(vyakti, logger=baselogger):
    vyakti.lastseen_timestamp = datetime.datetime.utcnow()
    vyakti.save()
    logger.info("{} sighted at {}".format(vyakti, utils.get_local_ts(vyakti.lastseen_timestamp).strftime("%Y-%m-%d %H:%M:%S")))


def create_abhivyakti(abhivyaktidict, logger=baselogger):
    if validate_abhivyakti_dict(abhivyaktidict)['status']:
        vyakti = documents.Vyakti.objects(vyakti_id=abhivyaktidict['vyakti_id'])
        if len(vyakti) > 0:
            vyakti = vyakti[0]
            abhivyaktidict.pop("vyakti_id")
        else:
            logger.error("No such Vyakti")
            return "No such Vyakti"
        try:
            abhivyakti = documents.AbhiVyakti(vyakti, **abhivyaktidict)
            abhivyakti.save()
            logger.info("{} created for {}".format(abhivyakti, vyakti))
            return abhivyakti
        except Exception as e:
            logger.error("{} {}".format(type(e), str(e)))
            return "{} {}".format(type(e), str(e))


def sighted_abhivyakti(abhivyakti, logger=baselogger):
    abhivyakti.lastseen_timestamp = datetime.datetime.utcnow()
    abhivyakti.save()
    logger.info("{} sighted at {}".format(abhivyakti, abhivyakti.lastseen_timestamp.strftime("%Y-%m-%d %H:%M:%S")))


def fb_get_profile_data(fbbrowser, url, logger=baselogger):
    profiledata = {}
    profilepic = {}
    fbbrowser.get(url)
    xetrapal.karma.wait()
    profile = fbbrowser.current_url
    if profile == "http://www.facebook.com/profile.php":
        plink = fbbrowser.find_element_by_xpath("//a[@title='Profile']")
        profile = plink.get_attribute("href")
    profiledata['url'] = profile
    profiledata['fbdisplayname'] = fb_get_cur_page_displayname(fbbrowser)
    fbbrowser.find_element_by_class_name("profilePicThumb").click()
    xetrapal.karma.wait()
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
        localfile = xetrapal.karma.download_file(
            profilepic['src'], prefix=profiledata['fbdisplayname'].replace(" ", ""), suffix=".jpg")
        profilepic['localfile'] = localfile
    except Exception as e:
        logger.error("Failed to download {} {}".format(type(e), str(e)))
    profiledata['tabdata'] = fb_get_profile_tab_data(fbbrowser, url)
    profiledata['friendcount'] = profiledata['tabdata']['friends']['count']
    profiledata['profilepic'] = profilepic
    return profiledata


def fb_get_profile_tab_data(fbbrowser, profileurl):
    tabdata = {"friends": {}, "photos": {}, "about": {}}
    fbbrowser.get(profileurl)
    xetrapal.karma.wait()
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


def fb_get_cur_page_displayname(fbbrowser):
    displayname = fbbrowser.find_element_by_id("fb-timeline-cover-name").find_element_by_tag_name("a").text
    return displayname


def fb_like_page_toggle(fbbrowser, pageurl):
    fbbrowser.get(pageurl)
    likebutton = fbbrowser.find_element_by_xpath("//button[@data-testid='page_profile_like_button_test_id']")
    likebutton.click()
