import string
import random

# from http://d.hatena.ne.jp/odz/20070821/1187682903
alphabets = string.digits + string.letters
def randstr(n):
    return ''.join(random.choice(alphabets) for i in xrange(n))
