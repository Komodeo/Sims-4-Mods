# decompyle3 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\google\protobuf\service.py
# Compiled at: 2011-01-23 23:39:36
# Size of source mod 2**32: 9357 bytes
__author__ = 'petar@google.com (Petar Petrov)'

class RpcException(Exception):
    pass


class Service(object):

    def GetDescriptor():
        raise NotImplementedError

    def CallMethod(self, method_descriptor, rpc_controller, request, done):
        raise NotImplementedError

    def GetRequestClass(self, method_descriptor):
        raise NotImplementedError

    def GetResponseClass(self, method_descriptor):
        raise NotImplementedError


class RpcController(object):

    def Reset(self):
        raise NotImplementedError

    def Failed(self):
        raise NotImplementedError

    def ErrorText(self):
        raise NotImplementedError

    def StartCancel(self):
        raise NotImplementedError

    def SetFailed(self, reason):
        raise NotImplementedError

    def IsCanceled(self):
        raise NotImplementedError

    def NotifyOnCancel(self, callback):
        raise NotImplementedError


class RpcChannel(object):

    def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        raise NotImplementedError