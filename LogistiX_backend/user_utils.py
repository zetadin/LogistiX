# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

import hashlib

def user_hash(user):
    d = f"{user.username}{user.date_joined}"
    h = hashlib.sha256(bytes(d, 'utf-8'))
    return(h.hexdigest())

def fast_hash_mod(num, mod=16):
    h = hashlib.md5(num.to_bytes(16, 'little', signed=False))
    val = int(h.hexdigest(), 16)
    return(val % mod)

def th(n):
    if(n%100 >10 and n%100<20):
        return "th"
    elif(n%10==1):
        return "st"
    elif(n%10==2):
        return "nd"
    elif(n%10==3):
        return "rd"
    else:
        return "th"
