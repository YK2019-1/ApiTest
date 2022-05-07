# -*- coding:utf-8 -*-
"""
=============================
# @Time : 2022/1/13 9:19 
# @Author : BadApple
# @File : test.py 
=============================
"""
from Myapp.models import *

def leetcode(nums):
    if len(nums) == 1:
        return 0
    nums1 = sorted(nums,reverse=True)
    if nums1[0] >= nums1[1]*2:
        return nums.index(nums1[0])
    else:
        return -1

def updata():
    DB_project.objects.filter(id=8).update(local_variable_id=0)

if __name__ == '__main__':
    nums = [3, 6, 1, 0]
    updata()

