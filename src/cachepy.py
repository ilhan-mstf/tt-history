# coding=utf-8

"""
retrieved from http://bjk5.com/post/2320616424/layer-caching-in-app-engine-with-memcache-and
"""

"""
Author: Juan Pablo Guereca

Module which implements a per GAE instance data cache, similar to what you can achieve with APC in PHP instances.

Each GAE instance caches the global scope, keeping the state of every variable on the global scope. 
You can go farther and cache other things, creating a caching layer for each GAE instance, and it's really fast because
there is no network transfer like in memcache. Moreover GAE doesn't charge for using it and it can save you many memcache
and db requests. 

Not everything are upsides. You can not use it on every case because: 

- There's no way to know if you have set or deleted a key in all the GAE instances that your app is using. Everything you do
  with Cachepy happens in the instance of the current request and you have N instances, be aware of that.
- The only way to be sure you have flushed all the GAE instances caches is doing a code upload, no code change required. 
- The memory available depends on each GAE instance and your app. I've been able to set a 60 millions characters string which
  is like 57 MB at least. You can cache somethings but not everything. 
"""

import time
import logging
import os

CACHE = {}
STATS_HITS = 0
STATS_MISSES = 0
STATS_KEYS_COUNT = 0

""" Flag to deactivate it on local environment. """
#ACTIVE = False if os.environ.get('SERVER_SOFTWARE').startswith('Devel') else True
ACTIVE = True

""" 
None means forever.
Value in seconds.
"""
DEFAULT_CACHING_TIME = None

"""
Curious thing: A dictionary in the global scope can be referenced and changed inside a function without using the global statement,
but it can not be redefined.
"""

def get( key ):
    """ Gets the data associated to the key or a None """
    if ACTIVE is False:
        return None
        
    global CACHE, STATS_MISSES, STATS_HITS
        
    """ Return a key stored in the python instance cache or a None if it has expired or it doesn't exist """
    if key not in CACHE:
        STATS_MISSES += 1
        return None
    
    value, expiry = CACHE[key]
    current_timestamp = time.time()
    if expiry == None or current_timestamp < expiry:
        STATS_HITS += 1
        return value
    else:
        STATS_MISSES += 1
        delete( key )
        return None

def set( key, value, expiry = DEFAULT_CACHING_TIME ):
    """
    Sets a key in the current instance
    key, value, expiry seconds till it expires 
    """
    if ACTIVE is False:
        return None
    
    global CACHE, STATS_KEYS_COUNT
    if key not in CACHE:
        STATS_KEYS_COUNT += 1
    if expiry is not None:
        expiry = time.time() + int( expiry )
    
    try:
        CACHE[key] = ( value, expiry )
    except MemoryError:
        """ It doesn't seem to catch the exception, something in the GAE's python runtime probably """
        logging.info( "%s memory error setting key '%s'" % ( __name__, key ) )
 
def delete( key ):
    """ 
    Deletes the key stored in the cache of the current instance, not all the instances.
    There's no reason to use it except for debugging when developing, use expiry when setting a value instead.
    """
    global CACHE, STATS_KEYS_COUNT
    if key in CACHE:
        STATS_KEYS_COUNT -= 1
        del CACHE[key]

def dump():
    """
    Returns the cache dictionary with all the data of the current instance, not all the instances.
    There's no reason to use it except for debugging when developing.
    """
    global CACHE
    return CACHE

def flush():
    """
    Resets the cache of the current instance, not all the instances.
    There's no reason to use it except for debugging when developing.
    """
    global CACHE, STATS_KEYS_COUNT
    CACHE = {}
    STATS_KEYS_COUNT = 0
    
def stats():
    """ Return the hits and misses stats, the number of keys and the cache memory address of the current instance, not all the instances."""
    global CACHE, STATS_MISSES, STATS_HITS, STATS_KEYS_COUNT
    memory_address = "0x" + str("%X" % id( CACHE )).zfill(16)
    return {'cache_memory_address': memory_address,
            'hits': STATS_HITS,
            'misses': STATS_MISSES ,
            'keys_count': STATS_KEYS_COUNT,
            }
    
def cacheit( keyformat, expiry=DEFAULT_CACHING_TIME ):
    """ Decorator to memoize functions in the current instance cache, not all the instances. """
    def decorator( fxn ):
        def wrapper( *args, **kwargs ):
            key = keyformat % args[:keyformat.count('%')]
            data = get( key )
            if data is None:
                data = fxn( *args, **kwargs )
                set( key, data, expiry )
            return data
        return wrapper
    return decorator
