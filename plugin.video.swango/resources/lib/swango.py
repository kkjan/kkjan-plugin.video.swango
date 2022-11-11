#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Wrapper pre SWAN Go
"""
import json
from sys import platform
import requests
import datetime
import time
from xml.dom import minidom 
import codecs
from resources.lib.logger import *
import os



_COMMON_HEADERS = { "User-Agent" :	"okhttp/3.12.1",
                    "Connection": "Keep-Alive"}




class SwanGoException(Exception):
    def __init__(self, id):
        self.id = id


class UserNotDefinedException(SwanGoException):
    def __init__(self):
        self.id = 30601

class UserInvalidException(SwanGoException):
    def __init__(self):
        self.id = 30602

class TooManyDevicesException(SwanGoException):
    def __init__(self,detail):
        self.id = 30603
        self.detail = detail
       

class StreamNotResolvedException(SwanGoException):
    def __init__(self, detail):
        self.id = 30604
        self.detail = detail

class PairingException(SwanGoException):
    def __init__(self, detail):
        self.id = 30605
        self.detail = detail

class SWANGO:

    def __init__(self,username =None,password=None,device_token=None, device_type_code = None, model=None,name=None, serial_number=None, datapath=None,_epg_lang_=None):
        self.username = username
        self.password = password
        self._live_channels = {}
        self.device_token = device_token
        self.subscription_code = None
        self.locality = None
        self.offer = None
        self.device_type_code = device_type_code
        self.model = model
        self.name = name
        self.serial_number = serial_number
        self.channels=[]
        self.datapath = datapath
        self.lang = _epg_lang_

    def logdevicestartup(self):
        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        data = {'device_token' : self.device_token,
                'application': "3.1.12",
                'firmware': "22" }
        req = requests.post('https://backoffice.swan.4net.tv/api/device/logDeviceStart', json=data,headers=headers)
        j=req.json()
        return j['success']
        
 
    def pairingdevice(self):
        result=-1
        if not self.username or not self.password:
            raise UserNotDefinedException()
        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        data = {  'login' : self.username,
                'password' : self.password,
                'id_brand' : 1}
        
                    #Pairing device
        req = requests.post('https://backoffice.swan.4net.tv/api/device/pairDeviceByLogin', json=data,headers=headers)
        j = req.json()
        if j['success']==True:
            self.device_token=j['token']
            data = {'device_token' : self.device_token,
                    'device_type_code' : self.device_type_code,
                    'model' : self.model,
                    'name' : self.name,
                    'serial_number' : self.serial_number }
            req = requests.post('https://backoffice.swan.4net.tv/api/device/completeDevicePairing', json=data,headers=headers)
            return self.device_token
        elif "validation_errors" in j['message'] and j['success']==False:
            raise TooManyDevicesException(j['message']['validation_errors'][0])
        elif j['success']==False:
            raise UserInvalidException()
        else:
            raise PairingException('Detail: '+j['message'])

        
     

    def get_devicesetting(self):
        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        data = {'device_token' : self.device_token}
        req = requests.post('https://backoffice.swan.4net.tv/api/getDeviceSettings/', json=data, headers=headers)
        j = req.json()
        self._device_settings=j
        return self._device_settings

        
    def get_live_stream(self, ch_id):
        channels=self.getchannels()
        for ch in  channels:
            if ch_id == ch['id_epg']:
                return ch['content_source']
    
    def get_swango_stream(self, ch_id,start,end):
        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        data = {'device_token' : self.device_token,
                 'channel_id':ch_id,
                 'start':start,
                 'end':end}
        req = requests.get('https://backoffice.swan.4net.tv/contentd/api/device/getContent',data, headers=headers)
        j = req.json()
        return j['stream_uri']

    def getchannels(self):
        ch =list()
        p=os.path.join(self.datapath,'sources-channel.json')
        with open(p, 'r') as json_file:
            j = json.load(json_file)
            json_file.close()  

        p=os.path.join(self.datapath,'broadcast-epg.json')
        with open(p, 'r') as json_file:
            epg = json.load(json_file)
            json_file.close() 
        now=time.time()
        #datetimeformat=xbmc.getRegion('dateshort')+" "+xbmc.getRegion('time')
        datetimeformat=xbmc.getRegion('dateshort')+" "+"%H:%M"
        for channel in j['channels']:
            ch_ids=list(filter(lambda x:x["epg_id"]==channel['id_epg'],epg['broadcasts']))
            ch_ids1=list(filter(lambda x:x["endTimestamp"]>now,ch_ids))
            ch_ids_curr=list(filter(lambda x:x["startTimestamp"]<now,ch_ids1))
            ch_ids_next=list(filter(lambda x:x["startTimestamp"]==ch_ids_curr[0]['endTimestamp'],ch_ids1))
            logDbg(repr(ch_ids_curr))
            ch ={ 'name' : channel['name'],
                'prg_name': ch_ids_curr[0]['name'],
                'next_prg_name': ch_ids_next[0]['name'],
                'next_prg_start': datetime.datetime.fromtimestamp(int(ch_ids_next[0]['startTimestamp'])).strftime(datetimeformat),
                'next_prg_end': datetime.datetime.fromtimestamp(int(ch_ids_next[0]['endTimestamp'])).strftime(datetimeformat),
                'id_epg' : channel['id_epg'],
                'tvg-name' : channel['name'].replace(" ","_"),
                'start' : datetime.datetime.fromtimestamp(int(ch_ids_curr[0]['startTimestamp'])).strftime(datetimeformat),
                'end' : datetime.datetime.fromtimestamp(int(ch_ids_curr[0]['endTimestamp'])).strftime(datetimeformat),
                'tvg-logo' : "https://epg.swan.4net.tv/files/channel_logos/"+str(channel['id'])+".png",
                'content_source' :  channel['content_sources'][0]['stream_profile_urls']['adaptive'] }
            plot=''
            if 'episode_name' in ch_ids_curr[0]:
                plot+=ch_ids_curr[0]['episode_name']+'[CR]'
            elif 'description' in ch_ids_curr[0]:
                plot += ch_ids_curr[0]['description']
            ch['plot']=plot

            if 'thumbnail' in ch_ids_curr[0]: 
                ch['img'] = "https://epg.swan.4net.tv/files/program_photos/_300/"+str(ch_ids_curr[0]['thumbnail']['extension'])
            elif 'photos' in ch_ids_curr[0]:
                ch['img'] = "https://epg.swan.4net.tv/files/program_photos/_300/"+str(ch_ids_curr[0]['photos'][0]['extension'])
            else:
                ch['img'] = 'DefaultVideo.png'

            if'genre' in ch_ids_curr[0]:
                ch['genre']=ch_ids_curr[0]['genre']
            else:
                ch['genre']=''

            if'year' in ch_ids_curr[0]:
                ch['year']=ch_ids_curr[0]['year']
            else:
                ch['year']=None

            self.channels.append(ch)
        return self.channels    


    def getswangotags(self):
        subcats =[]
        sc=list
        p=os.path.join(self.datapath,'tags.json')
        with open(p, 'r') as json_file:
            j = json.load(json_file)
            json_file.close()  

            for scid in j['tags'].keys():
                sc ={ 'name' : j['tags'][scid]['name'],
                        'id_tag' : scid,
                      'type' : j['tags'][scid]['type']}
                if 'photo' in j['tags'][scid]:
                   sc['img'] = "https://epg.swan.4net.tv/files/program_photos/_300/"+str(j['tags'][scid]['photo']['extension'])
                else:
                     sc['img'] = 'DefaultVideoIcon.png'
                subcats.append(sc)
        return subcats  

    def getcontent(self,id,episode,q=None):
        subcats=list()
        p=os.path.join(self.datapath,'broadcast-channel.json')
        with open(p, 'r') as json_file:
            bec = json.load(json_file)
            json_file.close()   
       # epg_xml=minidom.parse(epgpath)
    
        fromdat=datetime.datetime.now()-datetime.timedelta(days=7)
        todat=datetime.datetime.now()
        fromdt=int((fromdat-datetime.datetime(1970,1,1)).total_seconds())
        todt=int((todat-datetime.datetime(1970,1,1)).total_seconds())
        epg_special='special_epg_from['+str(fromdt)+']'

        p=os.path.join(self.datapath,'broadcast-channel.json')
        with open(p, 'r') as json_file:
            bec = json.load(json_file)
            json_file.close()   
       # epg_xml=minidom.parse(epgpath)
        epg_id=''
        broad_ch_epg=bec["channel_groups"][0]['channels']
        for ch in broad_ch_epg:
                epg_id=epg_id+str(ch["id_epg"])+','
        epg_id=epg_id[:-1]

        if not episode:
            
            data={
                'lng':self.lang,
                'epg_id':epg_id,
                'tag_id':id,
                'from':fromdt,
                'to':todt,
                'limit':100,
                epg_special:epg_id
            }
            url='https://epg.swan.4net.tv/search?v=3.1&tagged_only=0'
        if q:
            data={
                'lng':self.lang,
                'epg_id':epg_id,
                'from':fromdt,
                'to':todt,
                'limit':100,
                epg_special:epg_id,
                'q':q
            }
            url='https://epg.swan.4net.tv/search?v=3.1&tagged_only=0'  

        if episode:
            data={
                'lng':self.lang,
                'id_broadcast':id,
                'epg_id':epg_id,
                'tag_id':id,
                'from':fromdt,
                'to':todt,
                'limit':100,
                epg_special:epg_id
            }
            url='https://epg.swan.4net.tv/export/program?&&loadFullDetail=1&limit_similar=30&loadFullDetail=1'
        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        req = requests.get(url, params=data, headers=headers)        
        j = req.json()
        logDbg('getcontent '+req.url)
        if  j['error']==True:
            raise StreamNotResolvedException(j['message'])
        else:
            if not episode:
                dat=j['broadcasts']
            else:
                dat=j['related_broadcasts']
            datetimeformat=xbmc.getRegion('dateshort')+" "+xbmc.getRegion('time')
            for br in dat:
                ch_id=list(filter(lambda x:x["id_epg"]==br['epg_id'],broad_ch_epg))
                isSeries=768 in br['tag_ids'] #768-id forSeries tag
                logDbg('isSeries'+ str(isSeries))
                sc ={ 'name' : br['name']+" - "+ch_id[0]['name']+": "+ datetime.datetime.fromtimestamp(int(br['startTimestamp'])).strftime(datetimeformat),
                        'ch_id' : ch_id[0]['id'],
                        'br_id':br['id'],
                        'start':br['startTimestamp'],
                        'end':br['endTimestamp'],
                        'date':br['start']}
                if 'thumbnail' in br: 
                    sc['img'] = "https://epg.swan.4net.tv/files/program_photos/_300/"+str(br['thumbnail']['extension'])
                elif 'photos' in br:
                    sc['img'] = "https://epg.swan.4net.tv/files/program_photos/_300/"+str(br['photos'][0]['extension'])
                else:
                    sc['img'] = 'DefaultVideo.png'
                if'description' in br:
                    sc['info']=br['description']
                else:
                    sc['info']=br['name']
                if'genre' in br:
                    sc['genre']=br['genre']
                else:
                    sc['genre']=''
                if'year' in br:
                    sc['year']=br['year']
                else:
                    sc['year']=None
                if isSeries:
                    sc['series']=1
                else:
                    sc['series']=0
                subcats.append(sc)
        return subcats  



    def generateplaylist(self, playlistpath):
        channels = self.getchannels()
        with codecs.open(playlistpath , 'w',encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for channel in channels:
                # for tvheadend
                # strtmp="#EXTINF:-1 tvg-id=\""+str(channel['id_epg'])+"\" tvg-logo=\"https://epg.swan.4net.tv/files/channel_logos/"+str(channel['id'])+".png\" channel=\""+channel['name']+" tvg-name=\""+channel['name']+"\","+channel['name']+"\npipe:///storage/.kodi/addons/tools.ffmpeg-tools/bin/ffmpeg -fflags +genpts -i \""+channel['content_sources'][0]['stream_profile_urls']['adaptive']+"\" -vcodec copy -acodec copy -f mpegts  -mpegts_service_type digital_tv -metadata service_provider="+str(channel['id'])+" -metadata service_name= pipe:1"

                # for IPTV Simple client
                strtmp="#EXTINF:-1 tvg-id=\""+str(channel['id_epg'])+"\" tvg-name=\""+channel['tvg-name']+"\" tvg-logo=\""+channel['tvg-logo']+"\", "+channel['name']+"\n"+channel['content_source']
                f.write("%s\n" % strtmp)

    def generateepg(self,days,epgpath):
        guide = minidom.Document() 
        tv = guide.createElement('tv') 
        
        #Get channels
        channels = self.getchannels()

        for chnl in channels:
            channel=guide.createElement('channel')
            channel.setAttribute('id',str(chnl['id_epg']))

            display_name=guide.createElement('display-name')
            display_name.setAttribute('lang','sk')
            display_name.appendChild(guide.createTextNode(chnl['name']))
            channel.appendChild(display_name)

            icon=guide.createElement('icon')
            icon.setAttribute('src',chnl['tvg-logo'])
            channel.appendChild(icon)

            tv.appendChild(channel)

        today=datetime.datetime.now().replace(hour=23,minute=0,second=0,microsecond=0)
        #today.replace(tzinfo='timezone.utc').astimezone(tz=None)
        fromdat=today-datetime.timedelta(days=1)
        todat=today+datetime.timedelta(days=days)
        fromdt=int((fromdat-datetime.datetime(1970,1,1)).total_seconds())
        todt=int((todat-datetime.datetime(1970,1,1)).total_seconds())

        p=os.path.join(self.datapath,'broadcast-channel.json')
        with open(p, 'r') as json_file:
            bec = json.load(json_file)
            json_file.close()   
       # epg_xml=minidom.parse(epgpath)
        epg_id=''
        broad_ch_epg=bec["channel_groups"][0]['channels']
        for ch in broad_ch_epg:
                epg_id=epg_id+str(ch["id_epg"])+','
        epg_id=epg_id[:-1]

        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        data={'lng':self.lang,
            "epg_id":epg_id,
            "from":str(fromdt),
            "to":str(todt)
             }

        req = requests.get('https://epg.swan.4net.tv/export/broadcast', params=data, headers=headers)
        logDbg('URL: '+req.url)
        j = req.json()

        with open(os.path.join(self.datapath,'broadcast-epg.json'), 'w') as json_file:
            json.dump(j, json_file)
            json_file.close()
  
        tz=time.timezone
        m, s = divmod(tz, 60)
        h, m = divmod(m, 60)
        if tz >=0:
            timez="+"+'{0:02d}'.format(h)+'{0:02d}'.format(m)
        else:
            timez='{0:03d}'.format(h)+'{0:02d}'.format(m)

        for prg in j['broadcasts']:
            programme=guide.createElement('programme')
            programme.setAttribute('channel',str(prg['epg_id']))
            startdt=datetime.datetime.utcfromtimestamp(prg['startTimestamp']+tz)
            programme.setAttribute('start',str(startdt.strftime("%Y%m%d%H%M%S " ))+timez)
            stopdt=datetime.datetime.utcfromtimestamp(prg['endTimestamp']+tz)
            programme.setAttribute('stop',str(stopdt.strftime("%Y%m%d%H%M%S "))+timez)
            
            
            title=guide.createElement('title')
            title.setAttribute('lang','sk')
            title.appendChild(guide.createTextNode(prg['name']))
            programme.appendChild(title)

            desc=guide.createElement('desc')
            desc.setAttribute('lang','sk')
            if 'description' in prg:
                desc.appendChild(guide.createTextNode(prg['description']))
            else:
                desc.appendChild(guide.createTextNode(" "))
            programme.appendChild(desc)
            

            dat=guide.createElement('year')
            if 'year' in prg:
                dat.appendChild(guide.createTextNode(str(prg['year'])))
            else:
                dat.appendChild(guide.createTextNode(" "))
            programme.appendChild(dat)
            

            category=guide.createElement('category')
            category.setAttribute('lang','sk')
            if 'genre' in prg:
                category.appendChild(guide.createTextNode(prg['genre']))
            elif 'format' in prg:
                category.appendChild(guide.createTextNode(prg['format']))
            else:
                category.appendChild(guide.createTextNode(" "))
            programme.appendChild(category)

            icon=guide.createElement('icon')
            if 'thumbnailUrl300' in prg:
                icon.setAttribute('src',str(j['image_server'])+str(prg['thumbnailUrl300']))
            programme.appendChild(icon)
            

            tv.appendChild(programme)

        guide.appendChild(tv) 

        xml_str = guide.toprettyxml(indent ="\t", encoding="utf-8")  
        #guide.toprettyxml(encoding="utf-8")

        with codecs.open(epgpath, "wb") as f: 
            f.write(xml_str)  

    def updatebroadcast(self):

        headers = _COMMON_HEADERS
        headers["Content-Type"] = "application/json;charset=utf-8"
        data = {'device_token' : self.device_token}
        req = requests.post('https://backoffice.swan.4net.tv/api/device/getAllChannelGroups', json=data, headers=headers)
        j = req.json()

        with open(os.path.join(self.datapath,'broadcast-channel.json'), 'w') as json_file:
            json.dump(j, json_file)
            json_file.close()


        data = {'device_token' : self.device_token}
        req = requests.post('https://backoffice.swan.4net.tv/api/device/getSources', json=data, headers=headers)
        j = req.json()
        
        if  j['success']==False:
            raise StreamNotResolvedException(j['message'])
        else:
            with open(os.path.join(self.datapath,'sources-channel.json'), 'w') as json_file:
                json.dump(j, json_file)
                json_file.close()

  
        data={"lng" :self.lang}
        req = requests.get('https://epg.swan.4net.tv/export/tag?',params=data, headers=headers)
        j = req.json()
        logDbg('getswangotags '+req.url)
        if  j['error']==True:
            raise StreamNotResolvedException(j['message'])
        else:
            with open(os.path.join(self.datapath,'tags.json'), 'w') as json_file:
                json.dump(j, json_file)
                json_file.close()