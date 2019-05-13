# -*- coding: utf-8 -*-

import time
from common import TestEngine, VersionandPublicKeyCheck

__all__ = ['RASTest']

class RASTest(VersionandPublicKeyCheck):

    def __init__(self, service, configuration, resources):
        super().__init__(service, configuration, resources)
        
        self.imageskwargs = {
            'memberid': self.conf['memberid'], 
            'cloud': self.conf['cloud']
        }

    def run(self):
        self.__rasrequester__ = TestEngine(self.origin)
        
        pubkey = self.__getpubkey__()

        token = self.__createtoken__(pubkey)
        self.__rasrequester__.addHeader('Fogbow-User-Token', token)
        
        try:
            super().run()
            
            self.getimages()
            self.getimagebyid()
            
            networkid = self.createnetwork()
            computeid = self.createcompute()
            volumeid = self.createvolume()

            attachment = self.createattachment(volumeid, computeid)
        except Exception as e:
            self.fail()
            print("Interruped execution due to runtime error")
            raise e
        finally:
            self.logresults()

    def getimages(self):
        self.starttest('GET Images')
        
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        images = res.keys()
        
        self.assertgt(len(images), 0)
        self.endtest()

    def getimagebyid(self):
        self.starttest('GET Image by id')
        
        res = self.__rasrequester__.get('images', **self.imageskwargs).json()
        images = list(res.keys())

        imageid = images[0]
        imagedata = self.__rasrequester__.getbyid('images', imageid, **self.imageskwargs).json()

        _id = imagedata['id']
        _name = imagedata['name']
        _size = imagedata['size']

        if self.asserteq(type(_id), str):
            self.assertgt(len(_id), 0)

        if self.asserteq(type(_name), str):
            self.assertgt(len(_name), 0)

        if self.asserteq(type(_size), int):
            self.assertgt(_size, 0)

        self.endtest()

    def createnetwork(self):
        self.starttest('POST network')
        
        body = self.resources['create_network']
        res = self.__rasrequester__.create('networks', body=body)
        
        self.assertlt(res.status_code, 400)
        
        self.endtest()
        
        ret = res.json()
        return ret['id']

    def createcompute(self):
        self.starttest('POST compute')
        
        body = self.resources['create_compute']
        res = self.__rasrequester__.create('compute', body=body)
        
        self.assertlt(res.status_code, 400)
        
        self.endtest()
        
        ret = res.json()
        return ret['id']

    def createvolume(self):
        self.starttest('POST volume')
        
        body = self.resources['create_volume']
        res = self.__rasrequester__.create('volume', body=body)
        
        self.assertlt(res.status_code, 400)
        
        ret = res.json()
        self.endtest()
        
        return ret['id']

    def createattachment(self, volumeid, computeid):
        self.starttest('POST attachment')
        
        body = self.__attachmentbodyrequests__(volumeid, computeid)
        res = self.__rasrequester__.create('attachment', body=body)
        
        self.assertlt(res.status_code, 400)
        
        print(res, res.json())
        
        self.endtest()
        ret = res.json()
        return ret['id']

    @classmethod
    def required_resources(self):
        return ['auth_credentials', 'create_network', 'create_compute',
            'create_volume']

    def __getpubkey__(self):
        res = self.__rasrequester__.get('public-key').json()
        return res['publicKey']

    def __createtoken__(self, pubkey):
        
        as_url = self.conf['as_url']
        asrequester = TestEngine(as_url)

        credentials = self.resources['auth_credentials']
        credentials['publicKey'] = pubkey
        
        res = asrequester.create('token', body=credentials).json()
        return res['token']

    def __attachmentbodyrequests__ (self, volumeid, computeid):
        return {
            "computeId": volumeid,
            "volumeId": computeid
        }