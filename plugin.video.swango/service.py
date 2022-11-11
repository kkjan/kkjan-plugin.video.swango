import sys
import datetime
import os
import time
import requests
import resources.lib.swango as swango
import resources.lib.logger as logger
import xbmc
import xbmcaddon
import xbmcvfs



class swangoMonitor(xbmc.Monitor):
    _addon = None
    _next_update = 0
    _scriptname = None

    def __init__(self):
        xbmc.Monitor.__init__(self)
        self._addon = xbmcaddon.Addon()
        self._scriptname = self._addon.getAddonInfo('name')
        ts = self._addon.getSetting('next_update')
        self._next_update = datetime.datetime.now() if ts == '' else datetime.datetime.fromtimestamp(float(ts))
        logger.logDbg("Get settings next_update")
    
    def __del__(self):
        logger.log('service destroyed')

    def notify(self, text, error=False):
        icon = 'DefaultIconError.png' if error else ''
        try:
            text = text.encode("utf-8") if type(text) is unicode else text
            xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self._addon.getAddonInfo('name').encode("utf-8"), text, icon))
        except NameError as e:
            xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self._addon.getAddonInfo('name'), text, icon))

    def onSettingsChanged(self):
        self._addon = xbmcaddon.Addon()  # refresh for updated settings!
        if not self.abortRequested():
            try:
                res = self.update()
                if res == 1:
                    self.notify(self._addon.getLocalizedString(30701),False)
                else:
                    self._addon.openSettings();
            except swango.SwanGoException as e:
                logger.logErr(e.detail)
                self.notify(self._addon.getLocalizedString(e.id), True)

    def schedule_next(self, seconds):
        dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        logger.log('Next update %s' % dt)
        self._next_update = dt

    def update(self):
        result =-1
        try:
            logger.log('Update started')
            _generate_playlist = 'true' == self._addon.getSetting("generate_playlist")
            _generate_epg = 'true' == self._addon.getSetting("generate_epg")                           
            _username_ = self._addon.getSetting("username")
            _password_ = self._addon.getSetting("password")
            _device_token_ = self._addon.getSetting("device_token")
            _device_type_code_ = self._addon.getSetting("device_type_code")
            _device_model_ = self._addon.getSetting("device_model")
            _device_name_ = self._addon.getSetting("device_name")
            _device_serial_number_ = self._addon.getSetting("device_serial_number")
            _epgdays_ = int(self._addon.getSetting("epgdays"))
            _epgpath_ = os.path.join(self._addon.getSetting("epgpath"),self._addon.getSetting("epgfile"))
            _playlistpath_ = os.path.join(self._addon.getSetting("playlistpath"),self._addon.getSetting("playlistfile"))
            _datapath_ = xbmcvfs.translatePath(self._addon.getAddonInfo('profile')) 
            _epg_lang_ = self._addon.getSetting("epg_lang")
            _swango_=swango.SWANGO(_username_, _password_,_device_token_,_device_type_code_,_device_model_,_device_name_,_device_serial_number_,_datapath_,_epg_lang_)
            if _swango_.logdevicestartup() ==True:
                _swango_.updatebroadcast()
                if _generate_playlist:
                    _swango_.generateplaylist(_playlistpath_)
                if _generate_epg:
                    _swango_.generateepg(_epgdays_,_epgpath_)
                result=1
            else:
                logger.logDbg('pairing device')
                _swango_.device_token=_swango_.pairingdevice()
                logger.logDbg("Device token: " +_swango_.device_token)
                self._addon.setSetting("device_token",_swango_.device_token)
                if _swango_.logdevicestartup() ==True:
                    self._addon.setSetting("device_token",_swango_.device_token)
                    _swango_.updatebroadcast()
                    if _generate_playlist:
                        _swango_.generateplaylist(_playlistpath_)
                    if _generate_epg:
                        _swango_.generateepg(_epgdays_,_epgpath_)
                    result=1
            
        except swango.UserNotDefinedException as e:
            logger.logErr(self._addon.getLocalizedString(e.id))
            self.notify(self._addon.getLocalizedString(e.id), True)
        except swango.UserInvalidException as e:
            logger.logErr(self._addon.getLocalizedString(e.id))
            self.notify(self._addon.getLocalizedString(e.id), True)
        except swango.TooManyDevicesException as e:
            logger.logErr(self._addon.getLocalizedString(e.id))
            self.notify(self._addon.getLocalizedString(e.id), True)
        except swango.PairingException as e:
            logger.logErr(self._addon.getLocalizedString(e.id))
            self.notify(self._addon.getLocalizedString(e.id), True)
        except swango.SwanGoException as e:
            logger.logErr(self._addon.getLocalizedString(e.id))
            self.notify(self._addon.getLocalizedString(e.id), True)

        logger.log('Update ended')
        return result

    def tick(self):
        if datetime.datetime.now() > self._next_update:
            try:
                self.schedule_next(12 * 60 * 60)
                res=self.update()
                if res==1:
                    self.notify(self._addon.getLocalizedString(30702),False)
                else:
                    self._addon.openSettings()
            except requests.exceptions.ConnectionError:
                self.schedule_next(60)
                logger.log('Can''t update, no internet connection')
                pass
            except swango.SwanGoException as e:
                logger.logErr(e.detail)
                self.notify("Unexpected error", True)

    def save(self):
        self._addon.setSetting('next_update', str(time.mktime(self._next_update.timetuple())))
        logger.log('Saving next update %s' % self._next_update)


if __name__ == '__main__':
    monitor = swangoMonitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            monitor.save()
            break
        monitor.tick()
