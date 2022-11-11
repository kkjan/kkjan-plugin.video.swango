import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
from urllib.parse import urlparse
from urllib.parse import parse_qsl
from uuid import getnode as get_mac
import swango
import logger

params = False
_addon = xbmcaddon.Addon('plugin.video.swango')
_scriptname_=_addon.getAddonInfo('name')
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])


_first_error_ = (_addon.getSetting('first_error') == "true")
_send_errors_ = (_addon.getSetting('send_errors') == "true")
_username_ = _addon.getSetting("username")
_password_ = _addon.getSetting("password")
_device_token_ = _addon.getSetting("device_token")
_device_type_code_ = _addon.getSetting("device_type_code")
_device_model_ = _addon.getSetting("device_model")
_device_name_ = _addon.getSetting("device_name")
_device_serial_number_ = _addon.getSetting("device_serial_number")
_epgdays_ = int(_addon.getSetting("epgdays"))
_epgpath_ = _addon.getSetting("epgpath")
_playlistpath_ = _addon.getSetting("playlistpath")
__datapath__ = xbmcvfs.translatePath( _addon.getAddonInfo('profile'))

###############################################################################
#     Remote debbuging
###############################################################################
REMOTE_DBG = False
# append pydev remote debugger
if REMOTE_DBG:
    try:
        sys.path.append(os.environ['HOME']+r'/.xbmc/system/python/Lib/pysrc')
        sys.path.append(os.environ['APPDATA']+r'/Kodi/system/python/Lib/pysrc')
        import pydevd
        pydevd.settrace('libreelec.local', port=5678, stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: Could not load pysrc!")
        sys.exit(1)


###############################################################################


##############################################################################
#     First running
###############################################################################

# First run
if not (_addon.getSetting("settings_init_done") == 'true'):
    DEFAULT_SETTING_VALUES = { 'send_errors' : 'false' }
    for setting in list(DEFAULT_SETTING_VALUES.keys()):
        val = _addon.getSetting(setting)
        if not val:
            _addon.setSetting(setting, DEFAULT_SETTING_VALUES[setting])
    _addon.setSetting("settings_init_done", "true")

###############################################################################


def notify(text, error=False):
    icon = 'DefaultIconError.png' if error else ''
    try:
        text = text.encode("utf-8") if type(text) is unicode else text
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (_addon.getAddonInfo('name').encode("utf-8"), text, icon))
    except NameError as e:
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (_addon.getAddonInfo('name'), text, icon))

logger.logDbg('Handle: '+sys.argv[1])



def list_channels():
    logger.log("Reading channels ..."+str(_handle))
    try:
        for channel in _swango.getchannels():
            list_item = xbmcgui.ListItem(label=channel['name'])
            list_item.setArt({'icon': "DefaultVideo.png",
                                'thumb': channel['tvg-logo']})
            list_item.setInfo('video', {'title': channel['name'],
                                        'genre': channel['name'],
                                        'mediatype': 'video'})
            url = '{0}?action=play&id={1}'.format(_url, channel['id_epg'])
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
        logErr(e.detail)
    return

def list_categories():
    logger.log("Settings categories ..."+str(_handle))

    list_item = xbmcgui.ListItem(label='Live')
    list_item.setArt({'icon': 'DefaultFolder.png'});
    url = '{0}?action=live'.format(_url)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    logger.logDbg("list channels: "+url)
    list_item = xbmcgui.ListItem(label='SwanGo')
    list_item.setArt({'icon': 'DefaultFolder.png'});
    url = '{0}?action=swango'.format(_url)
    logger.logDbg("list categories: "+url)
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)
    
def list_subcategories():
    logger.log("Reading subcategories ..."+str(_handle))
    try:
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
        logErr(e.detail)
    return

def list_content(id,isSeries=False):
    logger.log("Reading content ..."+str(_handle))
    try:
        if isSeries==True:
            cont= _swango.getcontent(id,True)
        else:
            cont= _swango.getcontent(id,False)
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
        logErr(e.detail)
    return

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
    logger.log('Executing SWANGO plugin ...')
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

    _swango=swango.SWANGO(_username_, _password_,_device_token_,_device_type_code_,_device_model_,_device_name_,_device_serial_number_,__datapath__)
    router(sys.argv[2][1:])

