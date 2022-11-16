import datetime
import time
import requests
from  resources.lib.swango import SwanGoException
import resources.lib.iptvsimplehelper as iptvsimplehelper
import resources.lib.progress as progressdialogBG
import resources.lib.logger as logger
import xbmc
import xbmcaddon
from resources.lib.functions import *



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
        logger.logDbg("Get settings next_update: "+self._next_update.strftime("%m/%d/%Y, %H:%M:%S"))
        self._updt_interval=int(self._addon.getSetting('update_interval'))
        self._iptv_simple_restart_ = 'true' == self._addon.getSetting("iptv_simple_restart")
        self._iptvsimple=iptvsimplehelper.IPTVSimple()


    def __del__(self):
        logger.log('service destroyed')

    def update(self):
        
        result =-1
        try:
            log('Update started')
            _generate_playlist = 'true' == self._addon.getSetting("generate_playlist")
            _generate_epg = 'true' == self._addon.getSetting("generate_epg")          
            self._iptv_simple_restart_ = 'true' == self._addon.getSetting("iptv_simple_restart")                 
            _username_ = self._addon.getSetting("username")
            _password_ = self._addon.getSetting("password")
            _device_token_ = self._addon.getSetting("device_token")
            _device_type_code_ = self._addon.getSetting("device_type_code")
            _device_model_ = self._addon.getSetting("device_model")
            _device_name_ = self._addon.getSetting("device_name")
            _device_serial_number_ = self._addon.getSetting("device_serial_number")
            _epghourspast_ = 24* int(self._addon.getSetting("epgdays.past"))
      
            if _epghourspast_<24:
                _epghourspast_=24
            _epghourssfuture_ = 24*int(self._addon.getSetting("epgdays.future"))
            if _epghourssfuture_<24:
                _epghourssfuture_=24
            _epgpath_ = os.path.join(self._addon.getSetting("epgpath"),self._addon.getSetting("epgfile"))
            _playlistpath_ = os.path.join(self._addon.getSetting("playlistpath"),self._addon.getSetting("playlistfile"))
            _datapath_ = xbmcvfs.translatePath(self._addon.getAddonInfo('profile')) 
            _epg_lang_ = self._addon.getSetting("epg_lang")
            pDialog=None
            _swango_=swango.SWANGO(username=_username_, password=_password_,device_token=_device_token_,device_type_code=_device_type_code_,model=_device_model_,name=_device_name_,serial_number=_device_serial_number_,datapath=_datapath_,epg_lang=_epg_lang_)
            
            if _swango_.logdevicestartup() ==True:
                pDialog = progressdialogBG.progressdialogBG(self._addon.getLocalizedString(30067),self._addon.getLocalizedString(30068))
                if pDialog:
                    _swango_.progress = pDialog
                    pDialog.setpercentrange(0,15)
                #_swango_.save_swango_jsons(hourspast=_epghourspast_,hoursfuture=_epghourssfuture_)
                if _generate_playlist:
                    if pDialog:
                        pDialog.setpercentrange(15,40)
                        pDialog.setpozition(0,message=self._addon.getLocalizedString(30069))
                    _swango_.generateplaylist(playlistpath=_playlistpath_)
                if _generate_epg:
                    if pDialog:
                        pDialog.setpercentrange(40,70)
                        pDialog.setpozition(0,message=self._addon.getLocalizedString(30070))
                    _swango_.generateepg(epgpath=_epgpath_,hourspast=_epghourspast_,hoursfuture=_epghourssfuture_)
                if self._iptv_simple_restart_ and(_generate_epg or _generate_playlist):
                    if pDialog:
                        pDialog.setpercentrange(70,100)
                        pDialog.setpozition(0,message=self._addon.getLocalizedString(30071))
                    self._iptvsimple.iptv_simple_restart() 
                result=1
                if pDialog:
                    pDialog.setpozition(100, message=self._addon.getLocalizedString(30072))
                    pDialog.close()

            else:
                logDbg('Pairing device:')
                _swango_.device_token=_swango_.pairingdevice()
                logDbg("Device token: " +_swango_.device_token)
                self._addon.setSetting("device_token",_swango_.device_token)
                if _swango_.logdevicestartup() ==True:
                    self._addon.setSetting("device_token",_swango_.device_token)
                    _swango_.save_swango_jsons(hourspast=_epghourspast_,hoursfuture=_epghourssfuture_)
                    if _generate_playlist:
                        _swango_.generateplaylist(playlistpath=_playlistpath_)
                    if _generate_epg:
                        _swango_.generateepg(epgpath=_epgpath_,hourspast=_epghourspast_,hoursfuture=_epghourssfuture_)
                    if self._iptv_simple_restart_ and(_generate_epg or _generate_playlist):
                        self._iptvsimple.iptv_simple_restart() 
                    result=1
            
        except swango.UserNotDefinedException as e:
            logErr(self._addon.getLocalizedString(e.id))
            notify(self._addon.getLocalizedString(e.id), True)
        except swango.UserInvalidException as e:
            logErr(self._addon.getLocalizedString(e.id))
            notify(self._addon.getLocalizedString(e.id), True)
        except swango.TooManyDevicesException as e:
            logErr(self._addon.getLocalizedString(e.id))
            notify(self._addon.getLocalizedString(e.id), True)
        except swango.PairingException as e:
            logErr(self._addon.getLocalizedString(e.id))
            notify(self._addon.getLocalizedString(e.id), True)
        except swango.SwanGoException as e:
            logErr(self._addon.getLocalizedString(e.id))
            notify(self._addon.getLocalizedString(e.id), True)
        finally:
            if pDialog:
                pDialog.close()

        log('Update ended')
        return result
        
    def onSettingsChanged(self):
        self._addon = xbmcaddon.Addon()  # refresh for updated settings!
        notify(self._addon.getLocalizedString(30703),False)
        if not self.abortRequested():
            try:
                logger.logDbg("Update started onSettingsChanged")
                self._updt_interval=int(self._addon.getSetting('update_interval'))
                
    
                res = self.update()
                if res == 1:
                    notify(self._addon.getLocalizedString(30701),False)
                    self.schedule_next(self._updt_interval * 60 * 60)
                    logger.logDbg("Update finished onSettingsChanged")
                else:
                    self._addon.openSettings();
            except SwanGoException as e:
                logger.logErr(e.detail)
                notify(self._addon.getLocalizedString(e.id), True)

    def schedule_next(self, seconds):
        dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        logger.log('Next update %s' % dt)
        self._next_update = dt

   

    def tick(self):
        if  self._iptvsimple.need_restart and self._iptv_simple_restart_ :
            self._iptvsimple.iptv_simple_restart() 

    
        if datetime.datetime.now() > self._next_update:
            try:
                logger.logDbg("Update started from auto scheduller")
                notify(self._addon.getLocalizedString(30703),False)
                self.schedule_next(self._updt_interval * 60 * 60)
                res=self.update()
                logger.logDbg("Update ended from auto scheduller")
                if res==1:
                    notify(self._addon.getLocalizedString(30702),False)
                else:
                    self._addon.openSettings()
            except requests.exceptions.ConnectionError:
                self.schedule_next(60)
                logger.log('Can''t update, no internet connection')
                pass
            except SwanGoException as e:
                logger.logErr(e.detail)
                notify("Unexpected error", True)

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
