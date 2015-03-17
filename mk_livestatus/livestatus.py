#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket


__all__ = ['Query', 'Socket']


class Query(object):
    def __init__(self, conn, resource):
        self._conn = conn
        self._resource = resource
        self._columns = []
        self._filters = []

    def call(self):
        return self._conn.call(str(self))

    def __str__(self):
        request = 'GET %s' % (self._resource)
        if self._columns and any(self._columns):
            request += '\nColumns: %s' % (' '.join(self._columns))
        if self._filters:
            for filter_line in self._filters:
                request += '\nFilter: %s' % (filter_line)
        request += '\nOutputFormat: python\nColumnHeaders: on\n'
        return request

    def columns(self, *args):
        self._columns = args
        return self

    def filter(self, filter_str):
        self._filters.append(filter_str)
        return self


class Socket(object):
    def __init__(self, peer):
        self.peer = peer

    def __getattr__(self, name):
        return Query(self, name)

    def call(self, request):
        try:
            if len(self.peer) == 2:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(self.peer)
            s.send(request)
            s.shutdown(socket.SHUT_WR)
            data = []
            rawdata = s.makefile().read()
            if rawdata:
                data = eval(rawdata)
            return [ dict(zip(data[0], value)) for value in data[1:] ]
        finally:
            s.close()
