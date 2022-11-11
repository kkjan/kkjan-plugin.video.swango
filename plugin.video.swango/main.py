import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
<<<<<<< HEAD
import xbmcvfs
from urllib.parse import urlparse
from urllib.parse import parse_qsl
=======
from urlparse import urlparse
from urlparse import parse_qsl
>>>>>>> parent of 13a7385 (v0.1.1)
from uuid import getnode as get_mac
import resources.lib.swango as swango
import resources.lib.logger as logger

params = False
_addon = xbmcaddon.Addon('plugin.video.swango')
_scriptname_=_addon.getAddonInfo('name')
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
logger.logDbg('Handle: '+sys.argv[1])   

def notify(text, error=False):
    icon = 'DefaultIconError.png' if error else ''
    try:
        text = text.encode("utf-8") if type(text) is unicode else text
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (_addon.getAddonInfo('name').encode("utf-8"), text, icon))
    except NameError as e:
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (_addon.getAddonInfo('name'), text, icon))

_username_ = _addon.getSetting("username")
_password_ = _addon.getSetting("password")
_device_token_ = _addon.getSetting("device_token")
_device_type_code_ = _addon.getSetting("device_type_code")
_device_model_ = _addon.getSetting("device_model")
_device_name_ = _addon.getSetting("device_name")
_device_serial_number_ = _addon.getSetting("device_serial_number")
_epg_lang_ = _addon.getSetting("epg_lang")
_datapath_ = xbmcvfs.translatePath( _addon.getAddonInfo('profile'))

if not _username_ or not _password_:
    not_usr_pwd_notice = xbmcgui.Dialog()
    not_usr_pwd_notice.ok(_addon.getLocalizedString(30601),_addon.getLocalizedString(30063))
    _addon.openSettings()

<<<<<<< HEAD
if not _device_token_:
    notify(_addon.getLocalizedString(30064),True)
    _addon.openSettings()
=======
###############################################################################


##############################################################################
#     First running
###############################################################################

# First run
if not (_addon.getSetting("settings_init_done") == 'true'):
    DEFAULT_SETTING_VALUES = { 'send_errors' : 'false' }
    for setting in DEFAULT_SETTING_VALUES.keys():
        val = _addon.getSetting(setting)
        if not val:
            _addon.setSetting(setting, DEFAULT_SETTING_VALUES[setting])
    _addon.setSetting("settings_init_done", "true")

###############################################################################




###############################################################################
# log settings
###############################################################################
def log(msg, level=xbmc.LOGDEBUG):
    if type(msg).__name__=='unicode':
        msg = msg.encode('utf-8')
    xbmc.log("[%s] %s"%(_scriptname_,msg.__str__()), level)

def logDbg(msg):
    log(msg,level=xbmc.LOGDEBUG)

def logErr(msg):
    log(msg,level=xbmc.LOGERROR)
###############################################################################

def notify(self, text, error=False):
    icon = 'DefaultIconError.png' if error else ''
    try:
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self._addon.getAddonInfo('name').encode("utf-8"), text, icon))
    except NameError as e:
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self._addon.getAddonInfo('name'), text, icon))


def reload_settings():
    #_addon.openSettings()
    try:
        global _first_error_
        _first_error_ = (_addon.getSetting('first_error') == "true")
        global _send_errors_
        _send_errors_ = (_addon.getSetting('send_errors') == "true")
        global _username_
        _username_ = _addon.getSetting("username")
        global _password_
        _password_ = _addon.getSetting("password")
        global _device_token_
        _device_token_ = _addon.getSetting("device_token")
        global _device_type_code_
        _device_type_code_ = _addon.getSetting("device_type_code")
        global _device_model_
        _device_model_ = _addon.getSetting("device_model")
        global _device_name_
        _device_name_ = _addon.getSetting("device_name")
        global _device_serial_number_
        _device_serial_number_ = _addon.getSetting("device_serial_number")
        global _epgdays_
        _epgdays_ = int(_addon.getSetting("epgdays"))
        global _epgpath_
        _epgpath_ = _addon.getSetting("epgpath")
        global _playlistpath_
        _playlistpath_ = _addon.getSetting("playlistpath")
        
        if _swango.logdevicestartup() ==True:
            _swango.generateplaylist(_playlistpath_)
            _swango.generateepg(_epgdays_,_epgpath_)
        else:
            token=_swango.pairingdevice()
            if _swango.logdevicestartup() ==True:  
                _addon.setSetting('device_token',token)
                _swango.generateplaylist(_playlistpath_)
                _swango.generateepg(_epgdays_,_epgpath_) 
        logDbg("Playlist and EPG Updated -main.py")

    except swango.ToManyDeviceError():
        notify("To many device in SWAN Go service registered",True)
    except swango.PairingError():
        notify("Pairing device error",True)
    except swango.AuthenticationError():
        notify("Authentication error. Check Username and password in settings",True)
>>>>>>> parent of 13a7385 (v0.1.1)



def list_channels():
<<<<<<< HEAD
    logger.log("Reading channels ..."+str(_handle))
    try:
        for channel in _swango.getchannels():
            list_item = xbmcgui.ListItem(label=channel['name'],)
            list_item.setArt({'icon': "DefaultVideo.png",
                            'thumb': channel['tvg-logo'],
                            'poster':channel['img']})
            plot=channel['start']+' - '+channel['end'] + '[CR]'
            plot+=channel['plot']+'[CR]'+'[CR]'
            plot+='[COLOR blue][B]'+_addon.getLocalizedString(30065)+'[/B][/COLOR] '+channel['next_prg_name']+' '+channel['next_prg_start']+' - '+channel['next_prg_end']+'[CR]'
            title= channel['name']+': [B]'+channel['prg_name']+'[/B] '+channel['start']+' - '+channel['end'] + '[CR]'

            list_item.setInfo('video', {'title':title,
                                        'genre': channel['genre'],
                                        'year': channel['year'],
                                        'plot':plot,
                                        'mediatype': 'video'})
            url = '{0}?action=playlive&id={1}'.format(_url, channel['id_epg'])
            logger.logDbg("list channels: "+url)
            logger.logDbg('tvg-logo: '+channel['tvg-logo'])
            list_item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(_handle)
    except swango.StreamNotResolvedException as e:
        notify(e.detail,True)
        logger.logErr(e.detail)
    return

def list_categories():
    logger.log("Settings categories ..."+str(_handle))

    list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30060))
    list_item.setArt({'icon': 'DefaultFolder.png'});
    url = '{0}?action=live'.format(_url)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    logger.logDbg("list channels: "+url)
    list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30061))
    list_item.setArt({'icon': 'DefaultFolder.png'});
    url = '{0}?action=swango'.format(_url)
    logger.logDbg("list categories: "+url)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

=======
    xbmc.log("Reading channels ...", level=xbmc.LOGNOTICE)
    xbmcplugin.setPluginCategory(_handle, 'TV')
    xbmcplugin.setContent(_handle, 'videos')
    for channel in _swango.getchannels():
        list_item = xbmcgui.ListItem(label=channel['name'])
        list_item.setArt({'thumb': channel['tvg-logo'],
                        'icon': channel['tvg-logo']})
        list_item.setInfo('video', {'title': channel['name'],
                                    'genre': channel['name'],
                                    'mediatype': 'video'})
        url = '{0}?action=play&id={1}'.format(_url, channel['id_epg'])
        logDbg("list channels: "+url)
        list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
>>>>>>> parent of 13a7385 (v0.1.1)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)
<<<<<<< HEAD
    
def list_subcategories():
    logger.log("Reading subcategories ..."+str(_handle))
    try:
        list_item = xbmcgui.ListItem(label=_addon.getLocalizedString(30062))
        list_item.setArt({'icon': "DefaultAddonsSearch.png",
                                'thumb': "DefaultAddonsSearch.png"})
        url = '{0}?action=search'.format(_url)
        list_item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

        for subcat in _swango.getswangotags():
            list_item = xbmcgui.ListItem(label=subcat['name'])
            list_item.setArt({'icon': "DefaultVideo.png",
                                'thumb': subcat['img']})
            list_item.setInfo('video', {'title': subcat['name'],
                                        'genre': subcat['name'],
                                        'mediatype': 'video'})
            url = '{0}?action=tagcontent&id={1}&type={2}'.format(_url, subcat['id_tag'],subcat['type'])
            list_item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(_handle)
    except swango.StreamNotResolvedException as e:
        notify(e.detail,True)
        logger.logErr(e.detail)
    return

def list_content(id,isSeries=False,q=None):
    logger.log("Reading content ..."+str(_handle))
    try:
        if isSeries==True:
            cont= _swango.getcontent(id,True,q)
        else:
            cont= _swango.getcontent(id,False,q)
        for subcat in cont:
            list_item = xbmcgui.ListItem(label=subcat['name'])
            list_item.setArt({'icon': subcat['img'],
                                'thumb': subcat['img'],
                                'poster': subcat['img'],
                                'fanart': subcat['img']})
            list_item.setInfo('video', {'title': subcat['name'],
                                        'genre': subcat['genre'],
                                        'plot':subcat['info'],
                                        'year':subcat['year'],
                                        'dateadded':subcat['date'],
                                        'mediatype': 'video'})
            logger.logDbg('list_content: '+subcat['img'])
            
            if subcat['series']==0 or isSeries:
                isFolder=False
                url = '{0}?action=playswango&id={1}&start={2}&end={3}'.format(_url, subcat['ch_id'],subcat['start'],subcat['end'])
            else:
               isFolder=True
               url = '{0}?action=getepisodes&id={1}&SeriesFolder={2}'.format(_url, subcat['br_id'],'1')
            list_item.setProperty('IsPlayable', 'true')
            logger.logDbg('list_content: '+subcat['name'])
            logger.logDbg(isFolder)
            logger.logDbg(url)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, isFolder)
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_DATEADDED )
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_UNSORTED )
        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(_handle)
    except swango.StreamNotResolvedException as e:
        notify(e.detail,True)
        logger.logErr(e.detail)
    return
=======

>>>>>>> parent of 13a7385 (v0.1.1)

def list_search():
    keyboard = xbmc.Keyboard('', _addon.getLocalizedString(30062))
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        txt = keyboard.getText()
        list_content(0,False,txt)
        

def play_live(id):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    logger.logDbg("play_live: "+str(id))
    url = _swango.get_live_stream(int(id))

    logger.log('Playing channel ...')
    logger.log(str(url))
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


    # based on example from https://forum.kodi.tv/showthread.php?tid=330507
    # play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    # play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    # play_item.setMimeType('application/dash+xml')
    # play_item.setContentLookup(False)

    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def play_swango(id,start,end):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    logger.logDbg("play_swango "+str(id)+' start '+str(start)+' end '+str(end))
    url = _swango.get_swango_stream(int(id),start,end)

    logger.log('Playing channel ...')
    logger.log(str(url))
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


    # based on example from https://forum.kodi.tv/showthread.php?tid=330507
    # play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
    # play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    # play_item.setMimeType('application/dash+xml')
    # play_item.setContentLookup(False)

    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
<<<<<<< HEAD
    logger.log('Executing SWANGO plugin ...')
=======
    log('Executing SWANGO plugin ...', level=xbmc.LOGNOTICE)
>>>>>>> parent of 13a7385 (v0.1.1)
    params = dict(parse_qsl(paramstring))
    logger.logDbg(paramstring)
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'playlive':
            # Play a video from a provided URL.
            play_live(params['id'])
        elif params['action']=='playswango':
            play_swango(params['id'],params['start'],params['end'])
        elif params['action']=='live':
            list_channels()
        elif params['action']=='swango':
            list_subcategories()
        elif params['action']=='getepisodes':
            list_content(params['id'],True)
        elif params['action']=='search':
            list_search()
        elif params['action']=='tagcontent':
            list_content(params['id'],False)
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        #list_videos('Cars')
        list_categories()
        #list_channels()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring

    _swango=swango.SWANGO(_username_, _password_,_device_token_,_device_type_code_,_device_model_,_device_name_,_device_serial_number_,_datapath_,_epg_lang_)
    router(sys.argv[2][1:])

