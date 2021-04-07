# coding=utf-8
from . random_abstract import RandomData
import random

__all__ = ['AgeRandom']

class AgeRandom(RandomData):
    """年龄生成器（18到60岁）"""
    def create(self):
        return random.randrange(18, 60)
