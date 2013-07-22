'''
    universal XBMC module
    Copyright (C) 2013 the-one @ XBMC.org / XBMCHUB.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import xbmcgui,xbmcaddon,xbmc,xbmcplugin,time,datetime,os,re,urllib2

addon = xbmcaddon.Addon(id='script.module.universal')

import _common as common

class GA:

    _addon_id = ''
    _addon = ''
    
    _ga_track_id = ''
    _ga_begin_path = ''
    
    def __init__(self, addon_id, ga_track_id, path=''):

        addon.setSetting('ga_notified', '0')
        addon.setSetting('ga_enable', '1')
        
        self._addon_id = addon_id
        self._addon = xbmcaddon.Addon(id=addon_id)
        
        self._ga_track_id = ga_track_id       
        if path:
            self._ga_begin_path = path
        else:
            self._ga_begin_path = addon_id[addon_id.rfind('.')+1:]
            
        self.notified = True
        if int(addon.getSetting('ga_notified')) > 0:
            self.notified = False
            
        if self.notified == False:
            common.TextBoxes('Google Analytics', 
                'Google Analytics is used by the developers to track activity within the ADDON. It will share your IP Address as well as what sections you visit.\n\n'+
                'This is the only time you will receive this notification. You can change your selection by updating the setting: Addon Settings >> Universal Settings >> Google Analytics >> Enable Tracking to Yes or No.'
                )
            ga_notf_dlg = xbmcgui.Dialog()
            response = ga_notf_dlg.yesno('Google Analytics', 
                'Would you like to share your information?',
                nolabel='No',
                yeslabel='Yes')
            if response == True:
                addon.setSetting('ga_enable', '0')
            else:
                addon.setSetting('ga_enable', '1')
            self.notified = False
            addon.setSetting('ga_notified', '0')
            xbmc.executebuiltin( "Action(PreviousMenu)")
        
        self.enabled = True
        if int(addon.getSetting('ga_enable')) > 0:
            self.enabled = False
        
        if addon.getSetting('ga_visitor')=='':
            from random import randint
            addon.setSetting('ga_visitor',str(randint(0, 0x7fffffff)))
            
        self.check_GA()

    def parse_date(self, dateString):
        try:
            return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
        except:
            return datetime.datetime.today() - datetime.timedelta(days = 1) #force update


    def check_GA(self):
    
        if self.enabled == False:
            print "============================ GOOGLE ANALYTICS DISABLED ============================"
            return

        secsInHour = 60 * 60
        threshold  = 2 * secsInHour

        now   = datetime.datetime.today()
        prev  = self.parse_date(addon.getSetting('ga_time'))
        delta = now - prev
        nDays = delta.days
        nSecs = delta.seconds

        doUpdate = (nDays > 0) or (nSecs > threshold)
        if not doUpdate:
            return

        addon.setSetting('ga_time', str(now).split('.')[0])
        
        self.app_launch()
    
                    
    def send_request_to_google_analytics(self, utm_url):
        if self.enabled == False:
            print "============================ GOOGLE ANALYTICS DISABLED ============================"
            return
            
        ua='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
        import urllib2
        try:
            req = urllib2.Request(utm_url, None,
                                        {'User-Agent':ua}
                                         )
            response = urllib2.urlopen(req).read()
        except:
            print ("GA fail: %s" % utm_url)         
        return response
       
    def GA(self, group, name):
        if self.enabled == False:
            print "============================ GOOGLE ANALYTICS DISABLED ============================"
            return
            
        try:
            VISITOR = addon.getSetting('ga_visitor')            
            VERSION = self._addon.getAddonInfo('version')
            UATRACK = self._ga_track_id
            PATH = self._ga_begin_path
            
            try:
                from hashlib import md5
            except:
                from md5 import md5
            from random import randint
            import time
            from urllib import unquote, quote
            from os import environ
            from hashlib import sha1
            
            utm_gif_location = "http://www.google-analytics.com/__utm.gif"
            if not group=="None":
                    utm_track = utm_gif_location + "?" + \
                            "utmwv=" + VERSION + \
                            "&utmn=" + str(randint(0, 0x7fffffff)) + \
                            "&utmt=" + "event" + \
                            "&utme="+ quote("5("+PATH+"*"+group+"*"+name+")")+\
                            "&utmp=" + quote(PATH) + \
                            "&utmac=" + UATRACK + \
                            "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
                    try:
                        print "============================ POSTING TRACK EVENT ============================"
                        self.send_request_to_google_analytics(utm_track)
                    except:
                        print "============================  CANNOT POST TRACK EVENT ============================" 
            if name=="None":
                    utm_url = utm_gif_location + "?" + \
                            "utmwv=" + VERSION + \
                            "&utmn=" + str(randint(0, 0x7fffffff)) + \
                            "&utmp=" + quote(PATH) + \
                            "&utmac=" + UATRACK + \
                            "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
            else:
                if group=="None":
                       utm_url = utm_gif_location + "?" + \
                                "utmwv=" + VERSION + \
                                "&utmn=" + str(randint(0, 0x7fffffff)) + \
                                "&utmp=" + quote(PATH+"/"+name) + \
                                "&utmac=" + UATRACK + \
                                "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
                else:
                       utm_url = utm_gif_location + "?" + \
                                "utmwv=" + VERSION + \
                                "&utmn=" + str(randint(0, 0x7fffffff)) + \
                                "&utmp=" + quote(PATH+"/"+group+"/"+name) + \
                                "&utmac=" + UATRACK + \
                                "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
                                
            print "============================ POSTING ANALYTICS ============================"
            self.send_request_to_google_analytics(utm_url)
            
        except:
            print "================  CANNOT POST TO ANALYTICS  ================" 
            
            
    def app_launch(self):
    
        if self.enabled == False:
            print "============================ GOOGLE ANALYTICS DISABLED ============================"
            return
    
        VISITOR = addon.getSetting('ga_visitor')            
        VERSION = self._addon.getAddonInfo('version')
        UATRACK = self._ga_track_id
        PATH = self._ga_begin_path
        
        versionNumber = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
        if versionNumber < 12:
            if xbmc.getCondVisibility('system.platform.osx'):
                if xbmc.getCondVisibility('system.platform.atv2'):
                    log_path = '/var/mobile/Library/Preferences'
                else:
                    log_path = os.path.join(os.path.expanduser('~'), 'Library/Logs')
            elif xbmc.getCondVisibility('system.platform.ios'):
                log_path = '/var/mobile/Library/Preferences'
            elif xbmc.getCondVisibility('system.platform.windows'):
                log_path = xbmc.translatePath('special://home')
                log = os.path.join(log_path, 'xbmc.log')
                logfile = open(log, 'r').read()
            elif xbmc.getCondVisibility('system.platform.linux'):
                log_path = xbmc.translatePath('special://home/temp')
            else:
                log_path = xbmc.translatePath('special://logpath')
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
            match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        elif versionNumber > 11:
            print '======================= more than ===================='
            log_path = xbmc.translatePath('special://logpath')
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
            match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        else:
            logfile='Starting XBMC (Unknown Git:.+?Platform: Unknown. Built.+?'
            match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        print '==========================   '+PATH+' '+VERSION+'  =========================='

        try:
            from hashlib import md5
        except:
            from md5 import md5
        from random import randint
        import time
        from urllib import unquote, quote
        from os import environ
        from hashlib import sha1
        import platform

        for build, PLATFORM in match:
            if re.search('12',build[0:2],re.IGNORECASE): 
                build="Frodo" 
            if re.search('11',build[0:2],re.IGNORECASE): 
                build="Eden" 
            if re.search('13',build[0:2],re.IGNORECASE): 
                build="Gotham" 
            print build
            print PLATFORM
            utm_gif_location = "http://www.google-analytics.com/__utm.gif"
            utm_track = utm_gif_location + "?" + \
                    "utmwv=" + VERSION + \
                    "&utmn=" + str(randint(0, 0x7fffffff)) + \
                    "&utmt=" + "event" + \
                    "&utme="+ quote("5(APP LAUNCH*"+build+"*"+PLATFORM+")")+\
                    "&utmp=" + quote(PATH) + \
                    "&utmac=" + UATRACK + \
                    "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
            try:
                print "============================ POSTING APP LAUNCH TRACK EVENT ============================"
                self.send_request_to_google_analytics(utm_track)
            except:
                print "============================  CANNOT POST APP LAUNCH TRACK EVENT ============================" 

