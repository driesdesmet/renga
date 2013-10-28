import sys
import os
import random


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    return ''.join([random.SystemRandom().choice(allowed_chars) for i in range(length)])


def generate_key():
    """
    Generate a random key just like django-startproject does it.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*-_=+()'
    return get_random_string(50, chars)


