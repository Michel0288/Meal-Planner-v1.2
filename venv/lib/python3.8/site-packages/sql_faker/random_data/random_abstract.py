# coding=utf-8
from abc import ABCMeta, abstractmethod

__all__ = ['RandomData']

class RandomData:
    """随机值抽象类，子类必须实现create方法"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self):
        pass
