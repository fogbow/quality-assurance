# -*- coding: utf-8 -*-

import json
import requests
import time

from os import path
from . import HttpMethods, InstanceState

__all__ = ['FogbowHttpUtil', 'FogbowRequest']

class FogbowHttpUtil(object):
    def __init__(self, service_url):
        self.service_url = service_url
        self.body = {}
        self.headers = {}

    def wait_until_ready(self, resource, instance_id, **kwargs):
        tries = kwargs.get('tries', 50)
        if tries <= 0:
            return None
        
        res = self.getbyid(resource, instance_id, **kwargs)
        state = res.json()['state']
        if state == InstanceState.READY:
            ret = res
        else:
            time.sleep(1)
            kwargs['tries'] = tries-1
            ret = self.wait_until_ready(resource, instance_id, **kwargs)

        return ret

    def create(self, resource, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)

        headers = kwargs.get('headers', self.headers)
        body    = kwargs.get('body', self.body)

        req = FogbowRequest(url=url, headers=headers, body=body, method=str(HttpMethods.POST))
        return req.execute()

    def get(self, resource, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)
        
        return self.__execute__(url, **kwargs)

    def getall(self, resource, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)
        url += '/status'
        
        return self.__execute__(url, **kwargs)

    def getbyid(self, resource, _id, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)
        url += '/' + _id

        return self.__execute__(url, **kwargs)

    def delete(self, resource, _id, **kwargs):
        url = self.__getserviceendpoint__(resource, **kwargs)
        url += '/' + _id

        return self.__execute__(url, method=HttpMethods.DELETE, **kwargs)

    def __execute__(self, url, **kwargs):
        
        headers = kwargs.get('headers', self.headers)
        body    = kwargs.get('body', self.body)
        method  = kwargs.get('method', HttpMethods.GET)

        req = FogbowRequest(url=url, headers=headers, body=body, method=method)
        
        return req.execute()

    def __getserviceendpoint__(self, resource, **kwargs):
        memberid = kwargs.get('memberid')
        cloud = kwargs.get('cloud')
        pubip = kwargs.get('pubip')

        available_endpoints = {
            'token': '/tokens',
            'images': '/images/{}/{}/'.format(memberid, cloud),
            'members': '/members',
            'version': '/version',
            'public-key': '/publicKey',
            'network': '/networks',
            'compute': '/computes',
            'volume': '/volumes',
            'cloud': '/clouds',
            'public-ip': '/publicIps',
            'attachment': '/attachments',
            'secrule-publicip': '/publicIps/{}/securityRules/'.format(pubip)
        }

        urlpath = available_endpoints[resource]
        url = self.service_url + '/' + urlpath

        return url

    def addHeader(self, header, headervalue):
        if header and headervalue:
            print('Setting default header "{}" to "{}"'.format(header, headervalue))
            self.headers[header] = headervalue
        else:
            print("Ignoring header setting. One or more parameters were empty.")
            print("Header: {}".format(header))
            print("Header content: {}".format(headervalue))

class FogbowRequest:

    commonsettings = {
        'body': {}
    }

    def __init__(self, url, **kwargs):
        self.url = url
        self.headers = kwargs.get('headers', {})
        self.body = kwargs.get('body', {})
        self.method = kwargs.get('method', 'get')
        self.enablelog = kwargs.get('enablelog', True)

    @classmethod
    def addsetting(cls, key, setting):
        cls.commonsettings[key] = setting

    def execute(self):
        print("settings:", self.commonsettings)
        verb_requester = getattr(requests, self.method)

        body = {**self.body}

        if self.method == HttpMethods.POST:
            body = { **self.commonsettings, **body }

        res = verb_requester(url=self.url, json=body, headers=self.headers)

        if self.enablelog:
            print("\n{} {}".format(self.method.upper(), res.url, ))

        return res
