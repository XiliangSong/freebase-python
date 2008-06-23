# ==================================================================
# Copyright (c) 2007, Metaweb Technologies, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY METAWEB TECHNOLOGIES AND CONTRIBUTORS
# ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL METAWEB
# TECHNOLOGIES OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ====================================================================

"""
declarations for external metaweb api.


    from metaweb.api import HTTPMetawebSession

    mss = HTTPMetawebSession('sandbox.freebase.com')
    print mss.mqlread([dict(name=None, type='/type/type')])
"""



__all__ = ['MetawebError', 'MetawebSession', 'HTTPMetawebSession', 'attrdict']
__version__ = '0.1'

import os, sys, re
import cookielib
try:
    import simplejson
except ImportError:
    from django.utils import simplejson
try:
    from urllib import quote as urlquote
except ImportError:
    from urlib_stub import quote as urlquote
import pprint
import socket
import logging

class Delayed(object):
    """
    Wrapper for callables in log statements. Avoids actually making
    the call until the result is turned into a string.

    A few examples:

    simplejson.dumps is never called because the logger never
    tries to format the result
    >>> logging.debug(Delayed(simplejson.dumps, q))

    This time simplejson.dumps() is actually called:
    >>> logging.warn(Delayed(simplejson.dumps, q))
    
    """
    def __init__(self, f, *args, **kwds):
        self.f = f
        self.args = args
        self.kwds = kwds

    def __str__(self):
        return str(self.f(*self.args, **self.kwds))
    
def logformat(result):
    """
    Format the dict/list as a json object
    """
    rstr = simplejson.dumps(result, indent=2)
    if rstr[0] == '{':
        rstr = rstr[1:-2]
    return rstr

from httpclients import Httplib2Client, Urllib2Client, UrlfetchClient

# Check for urlfetch first so that urlfetch is used when running the appengine SDK
try:
    import google.appengine.api.urlfetch
    from cookie_handlers import CookiefulUrlfetch
    http_client = UrlfetchClient
except ImportError:
    try:
        import httplib2
        from cookie_handlers import CookiefulHttp
        http_client = Httplib2Client
    except ImportError:
        import urllib2
        httplib2 = None
        CookiefulHttp = None
        http_client = Urllib2Client
        print ('freebase.api: you can install httplib2 for better performance')

# remove whitespace from json encoded output
simplejson.JSONEncoder.item_separator = ','
simplejson.JSONEncoder.key_separator = ':'
# don't escape slashes, we're not pasting into script tags here.
if simplejson.encoder.ESCAPE_DCT.get('/', None) == r'\/':
    simplejson.encoder.ESCAPE_DCT['/'] = '/'

def urlencode_weak(s):
    return urlquote(s, safe=',/:$')


# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/361668
class attrdict(dict):
    """A dict whose items can also be accessed as member variables.

    >>> d = attrdict(a=1, b=2)
    >>> d['c'] = 3
    >>> print d.a, d.b, d.c
    1 2 3
    >>> d.b = 10
    >>> print d['b']
    10

    # but be careful, it's easy to hide methods
    >>> print d.get('c')
    3
    >>> d['get'] = 4
    >>> print d.get('a')
    Traceback (most recent call last):
    TypeError: 'int' object is not callable
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self



# TODO expose the common parts of the result envelope
class MetawebError(Exception):
    """
    an error report from the metaweb service.
    """
    pass



# TODO right now this is a completely unnecessary superclass.
#  is there enough common behavior between session types
#  to justify it?
class MetawebSession(object):
    """
    MetawebSession is the base class for MetawebSession, subclassed for
    different connection types.  Only http is available externally.

    This is more of an interface than a class
    """

    # interface definition here...
    

# from httplib2
NORMALIZE_SPACE = re.compile(r'(?:\r\n)?[ \t]+')
def _normalize_headers(headers):
    return dict([ (key.lower(), NORMALIZE_SPACE.sub(value, ' ').strip())  for (key, value) in headers.iteritems()])

class HTTPMetawebSession(MetawebSession):
    """
    a MetawebSession is a request/response queue.

    this version uses the HTTP api, and is synchronous.
    """
    # share cookies across sessions, so that different sessions can
    #  see each other's writes immediately.
    _default_cookiejar = cookielib.CookieJar()

    def __init__(self, service_url, username=None, password=None, prev_session=None, cookiejar=None, cookiefile=None):
        """
        create a new MetawebSession for interacting with the Metaweb.

        a new session will inherit state from prev_session if present, 
        """
        super(HTTPMetawebSession, self).__init__()

        self.log = logging.getLogger()

        assert not service_url.endswith('/')
        if not '/' in service_url:  # plain host:port
            service_url = 'http://' + service_url

        self.service_url = service_url

        self.username = username
        self.password = password

        self.tid = None

        if prev_session:
            self.service_url = prev.service_url

        if cookiefile is not None:
            cookiejar = self.open_cookie_file(cookiefile)

        if cookiejar is not None:
            self.cookiejar = cookiejar
        elif prev_session:
            self.cookiejar = prev_session.cookiejar
        else:
            self.cookiejar = self._default_cookiejar

        self._http_request = http_client(self.cookiejar)


    def open_cookie_file(self, cookiefile=None):
        if cookiefile is None or cookiefile == '':
            if os.environ.has_key('HOME'):
                cookiefile = os.path.join(os.environ['HOME'], '.pyfreebase/cookiejar')
            else:
                raise MetawebError("no cookiefile specified and no $HOME/.pyfreebase directory" % cookiefile)

        cookiejar = cookielib.LWPCookieJar(cookiefile)
        if os.path.exists(cookiefile):
            cookiejar.load(ignore_discard=True)

        return cookiejar


    def _httpreq(self, service_path, method='GET', body=None, form=None,
                 headers=None):
        """
        make an http request to the service.

        form arguments are encoded in the url, even for POST, if a non-form
        content-type is given for the body.

        returns a pair (resp, body)

        resp is the response object and may be different depending
        on whether urllib2 or httplib2 is in use?
        """

        if method == 'POST':
            assert body is not None or form is not None
        elif method == 'GET':
            assert body is None
        else:
            assert 0, 'unknown method %s' % method

        url = self.service_url + service_path

        if headers is None:
            headers = {}
        else:
            headers = _normalize_headers(headers)

        # XXX This is a lousy way to parse Content-Type, where is
        #  the library?
        ct = headers.get('content-type', None)
        if ct is not None:
            ct = ct.split(';')[0]

        if body is not None:
            # if body is provided, content-type had better be too
            assert ct is not None

        if form is not None:
            qstr = '&'.join(['%s=%s' % (urlencode_weak(k), urlencode_weak(v))
                             for k,v in form.items()])
            if method == 'POST':
                # put the args on the url if we're putting something else
                # in the body.  this is used to add args to raw uploads.
                if body is not None:
                    url += '?' + qstr
                else:
                    if ct is None:
                        # XXX encoding and stuff
                        ct = 'application/x-www-form-urlencoded'
                        headers['content-type'] = ct

                    if ct == 'multipart/form-encoded':
                        # XXX fixme
                        raise NotImplementedError
                    elif ct == 'application/x-www-form-urlencoded':
                        body = qstr
            else:
                # for all methods other than POST, use the url
                url += '?' + qstr


        # assure the service that this isn't a CSRF form submission
        headers['x-metaweb-request'] = 'Python'

        if 'user-agent' not in headers:
            headers['user-agent'] = 'python freebase.api-%s' % __version__

        #if self.tid is not None:
        #    headers['x-metaweb-tid'] = self.tid

        ####### DEBUG MESSAGE - should check log level before generating 
        if form is None:
            formstr = ''
        else:
            formstr = '\nFORM:\n  ' + '\n  '.join(['%s=%s' % (k,v)
                                          for k,v in form.items()])
        if headers is None:
            headerstr = ''
        else:
            headerstr = '\nHEADERS:\n  ' + '\n  '.join([('%s: %s' % (k,v))
                                              for k,v in headers.items()])
        self.log.info('%s %s%s%s', method, url, formstr, headerstr)
        #######

        return self._http_request(url, method, body, headers)

    def _raise_service_error(self, url, status, ctype, body):

        is_jsbody = (ctype.endswith('javascript')
                     or ctype.endswith('json'))
        if str(status) == '400' and is_jsbody:
            r = self._loadjson(body)
            msg = r.messages[0]
            raise MetawebError(u'%s %s %r' % (msg.get('code',''), msg.message, msg.info))

        raise MetawebError, 'request failed: %s: %r %r' % (url, status, body)
        
    def _httpreq_json(self, *args, **kws):
        resp, body = self._httpreq(*args, **kws)
        return self._loadjson(body)

    def _loadjson(self, json):
        # TODO really this should be accomplished by hooking
        # simplejson to create attrdicts instead of dicts.
        def struct2attrdict(st):
            """
            copy a json structure, turning all dicts into attrdicts.
            
            copying descends instances of dict and list, including subclasses.
            """
            if isinstance(st, dict):
                return attrdict([(k,struct2attrdict(v)) for k,v in st.items()])
            if isinstance(st, list):
                return [struct2attrdict(li) for li in st]
            return st

        if json == '':
            self.log.error('the empty string is not valid json')
            raise MetawebError('the empty string is not valid json')

        try:
            r = simplejson.loads(json)
        except ValueError, e:
            self.log.error('error parsing json string %r' % json)
            raise MetawebError, 'error parsing JSON string: %s' % e

        return struct2attrdict(r)

    def _check_mqlerror(self, r):
        if r.code != '/api/status/ok':
            for msg in r.messages:
                self.log.error('mql error: %s %s %r' % (msg.code, msg.message, msg.get('query', None)))
            raise MetawebError, 'query failed: %s\n%r' % (r.messages[0].code, r.messages[0].get('query', None))

    def _mqlresult(self, r):
        self._check_mqlerror(r)

        self.log.info('result: %s', Delayed(logformat, r))

        return r.result



    def login(self):
        """sign in to the service"""

        assert self.username is not None
        assert self.password is not None
        
        self.log.debug('LOGIN USERNAME: %s', self.username)
        
        try:
            r = self._httpreq_json('/api/account/login', 'POST',
                                   form=dict(username=self.username,
                                             password=self.password))
        except urllib2.HTTPError, e:
            raise MetawebError("login error: %s", e)

        if r.code != '/api/status/ok':
            raise MetawebError(u'%s %r' % (r.get('code',''), r.messages))

        self.log.debug('LOGIN RESP: %r', r)
        self.log.debug('LOGIN COOKIES: %s', self.cookiejar)


    def mqlreaditer(self, sq):
        """read a structure query"""

        cursor = True

        while 1:
            subq = dict(query=[sq], cursor=cursor, escape=False)
            qstr = simplejson.dumps(subq)

            service = '/api/service/mqlread'
            
            r = self._httpreq_json(service, form=dict(query=qstr))

            for item in self._mqlresult(r):
                yield item

            if r['cursor']:
                cursor = r['cursor']
                self.log.info('CONTINUING with %s', cursor)
            else:
                return

    def mqlread(self, sq):
        """read a structure query"""
        subq = dict(query=sq, escape=False)
        if isinstance(sq, list):
            subq['cursor'] = True

        service = '/api/service/mqlread'

        self.log.info('%s: %s',
                      service,
                      Delayed(logformat, sq))

        qstr = simplejson.dumps(subq)
        r = self._httpreq_json(service, form=dict(query=qstr))

        return self._mqlresult(r)

    def mqlreadmulti(self, queries):
        """read a structure query"""
        keys = [('q%d' % i) for i,v in enumerate(queries)];
        envelope = {}
        for i,sq in enumerate(queries):
            subq = dict(query=sq, escape=False)
            # XXX put this back once mqlreadmulti is working in general
            #if isinstance(sq, list):
            #    subq['cursor'] = True
            envelope[keys[i]] = subq

        service = '/api/service/mqlread'

        self.log.info('%s: %s',
                      service,
                      Delayed(logformat, envelope))

        qstr = simplejson.dumps(envelope)
        rs = self._httpreq_json(service, form=dict(queries=qstr))

        self.log.info('%s result: %s',
                      service,
                      Delayed(simplejson.dumps, rs, indent=2))

        return [self._mqlresult(rs[key]) for key in keys]

    def trans(self, guid):
        """translate blob from guid """
        url = '/api/trans/raw' + urlquote(guid)

        self.log.info(url)

        resp, body = self._httpreq(url)

        self.log.info('%d bytes' % len(body))

        return body

    def mqlwrite(self, sq):
        """do a mql write"""
        query = dict(query=sq, escape=False)
        qstr = simplejson.dumps(query)

        self.log.debug('MQLWRITE: %s', qstr)

        service = '/api/service/mqlwrite'

        self.log.info('%s: %s',
                      service,
                      Delayed(logformat,sq))

        r = self._httpreq_json(service, 'POST',
                               form=dict(query=qstr))

        self.log.debug('MQLWRITE RESP: %r', r)
        return self._mqlresult(r)

    def mqlcheck(self, sq):
        """ See if a write is valid, and see what would happen, but do not
        actually do the write """
        
        query = dict(query=sq, escape=False)
        qstr = simplejson.dumps(query)

        self.log.debug('MQLCHECK: %s', qstr)

        service = '/api/service/mqlcheck'

        self.log.info('%s: %s',
                      service,
                      Delayed(logformat, sq))

        r = self._httpreq_json(service, 'POST',
                               form=dict(query=qstr))


        self.log.debug('MQLCHECK RESP: %r', r)

        return self._mqlresult(r)
    
    def mqlflush(self):
        """ask the service not to hand us old data"""
        self.log.debug('MQLFLUSH')
    
        service = '/api/service/touch'
        r = self._httpreq(service, 'POST', body='',
                          headers={'content-type':'application/xml',
                                   'content-length':'0'})

        # TODO non-conforming service, fix later
        #self._check_mqlerror(r)
        return True

    def upload(self, body, content_type, document_id=False):
        """upload to the metaweb"""

        service = '/api/service/upload'

        self.log.info('POST %s: %s (%d bytes)',
                      service, content_type, len(body))


        headers = {}
        if content_type is not None:
            headers['content-type'] = content_type

        form = None
        if document_id is not False:
            if document_id is None:
                form = { 'document': '' }
            else:
                form = { 'document': document_id }

        # note the use of both body and form.
        #  form parameters get encoded into the URL in this case
        r = self._httpreq_json(service, 'POST',
                               headers=headers, body=body, form=form)
        return self._mqlresult(r)

    def reconcile(self, name, etype=['/common/topic']):
        """reconcile name to guid"""

        service = '/dataserver/reconciliation'
        r = self._httpreq_json(service, 'GET', form={'name':name, 'types':','.join(etype)})

        
        # TODO non-conforming service, fix later
        #self._mqlresult(r)
        return r

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    mss = HTTPMetawebSession('sandbox.freebase.com')

    self.mss.log.setLevel(logging.DEBUG)
    self.mss.log.addHandler(console)


    print mss.mqlread([dict(name=None, type='/type/type')])
