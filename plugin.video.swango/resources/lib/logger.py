import xbmc
import xbmcaddon


_addon = xbmcaddon.Addon('plugin.video.swango')
_scriptname_=_addon.getAddonInfo('name')

###############################################################################
# log settings
###############################################################################
def log(msg, level=xbmc.LOGINFO):
    if type(msg).__name__=='unicode':
        msg = msg.encode('utf-8')
    xbmc.log("[%s] %s"%(_scriptname_,msg.__str__()), level)

def logDbg(msg):
    log(msg,level=xbmc.LOGDEBUG)

def logErr(msg):
    log(msg,level=xbmc.LOGERROR)
###############################################################################
