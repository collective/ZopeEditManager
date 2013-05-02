#
#  ZopeEditController.py
#  ZopeEditManager
#
#  Created by Zachery Bir on 2003-08-20.
#  Copyright (c) 2004 Zope Foundation and Contributors.
#

# library imports
import sys, os, re
import urllib
from urlparse import urlparse
from httplib import HTTPConnection, HTTPSConnection
from tempfile import mktemp

# import needed classes/functions from Foundation
from Foundation import *

# import Nib loading functionality from AppKit
from AppKit import *

__version__ = u"0.9"

def fatalError(message):
    """Show error message and exit"""
    if NSRunAlertPanel('Sorry',
                       'Fatal Error: %s' % message,
                       'Quit', None, None):
        # Write out debug info to a temp file
        debug_f = open(mktemp('-zopeedit-traceback.txt'), 'w')
        try:
            traceback.print_exc(file=debug_f)
        finally:
            debug_f.close()
        sys.exit(0)

class ZopeDocument:

    def __init__(self, filename):
        self.filename = filename
        (self.metadata, self.contents) = self.getMetadataAndContents(filename)
        meta_type = self.metadata.get('meta_type', None)
        content_type = self.metadata.get('content_type', 'text/plain')

        self.sud = NSUserDefaults.standardUserDefaults()

        options_group = self.sud.dictionaryForKey_('helper_apps')

        self.options = options_group.get(meta_type,
                                    options_group.get(content_type, None))
        if not self.options:
            content_type, content_subtype = re.split(r'[/_]', content_type, 1)
            self.options = options_group.get("%s/*" % content_type)

        scheme, self.host, self.path = urlparse(self.metadata['url'])[:3]
        self.ssl = scheme == 'https'

        self.content_file = self.generateContentFile()

        self.last_mtime = os.path.getmtime(self.content_file)

        if self.ssl:
            # See if ssl is available
            try:
                from socket import ssl
            except ImportError:
                fatalError('SSL support is not available on this system. '
                           'Make sure openssl is installed '
                           'and reinstall Python.')

        self.saved = 1
        self.lock_token = None
        self.did_lock = 0

    def getEditor(self):
        return self.options['editor']

    def getContentFile(self):
        return self.content_file

    def getContentFileName(self):
        return os.path.split(self.content_file)[-1].split(',')[-1]

    def getFilename(self):
        return self.filename

    def generateContentFile(self):
        content_file = urllib.unquote('-%s%s' % (self.host, self.path))
        content_file = content_file.replace('/',
                                            ',').replace(':',
                                                         ',').replace(' ',
                                                                      '_')

        extension = self.options.get('extension', None)

        if extension and not content_file.endswith(extension):
            content_file = content_file + extension

        if self.sud.stringForKey_('temp_dir'):
            while 1:
                temp = os.path.expanduser(self.sud.stringForKey_('temp_dir'))
                temp = os.tempnam(temp)
                content_file = '%s%s' % (temp, content_file)
                if not os.path.exists(content_file):
                    break
        else:
            content_file = mktemp(content_file)

        out_f = open(content_file, 'wb')
        out_f.write(self.contents)
        out_f.close()

        return content_file

    def getMetadataAndContents(self, filename):
        metadata = {}

        in_f = open(filename, 'rb')

        # grab the metadata and build a dictionary
        while 1:
            line = in_f.readline()[:-1]
            if not line: break
            key, val = line.split(':', 1)
            metadata[key] = val

        # grab the rest and stick it in contents
        contents = in_f.read()

        in_f.close()

        return (metadata, contents)

    def removeFileIfNecessary(self, filename):
        if self.sud.boolForKey_('cleanup_files'):
            try:
                os.remove(filename)
            except OSError:
                pass # Sometimes we aren't allowed to delete it

    def putChanges(self):
        """Save changes to the file back to Zope"""
        if self.sud.boolForKey_('use_locks') and self.lock_token is None:
            # We failed to get a lock initially, so try again before saving
            if not self.lock():
                # Confirm save without lock
                if not NSRunAlertPanel('Lock Error',
                                       'Could not acquire lock. '
                                       'Attempt to save to Zope anyway?',
                                       'Yes', 'No', None):
                    return 0

        f = open(self.content_file, 'rb')
        body = f.read()
        f.close()
        headers = {'Content-Type':
                   self.metadata.get('content_type', 'text/plain')}

        if self.lock_token is not None:
            headers['If'] = '<%s> (<%s>)' % (self.path, self.lock_token)

        response = self.zopeRequest('PUT', headers, body)
        del body # Don't keep the body around longer then we need to

        if response.status / 100 != 2:
            # Something went wrong
            message = response.read()
            NSLog(message)
            if NSRunAlertPanel(message,
                               'Could not save to Zope.\n'
                               'Error occurred during HTTP put',
                               'Retry', 'Cancel', None):
                return self.putChanges()
            else:
                return 0
        return 1

    def lock(self):
        """Apply a webdav lock to the object in Zope"""
        if self.lock_token is not None:
            return 0 # Already have a lock token

        headers = {'Content-Type':'text/xml; charset="utf-8"',
                   'Timeout':'infinite',
                   'Depth':'infinity',
                  }
        body = ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<d:lockinfo xmlns:d="DAV:">\n'
                '  <d:lockscope><d:exclusive/></d:lockscope>\n'
                '  <d:locktype><d:write/></d:locktype>\n'
                '  <d:depth>infinity</d:depth>\n'
                '  <d:owner>\n'
                '  <d:href>Zope External Editor</d:href>\n'
                '  </d:owner>\n'
                '</d:lockinfo>'
                )

        response = self.zopeRequest('LOCK', headers, body)

        if response.status / 100 == 2:
            # We got our lock, extract the lock token and return it
            reply = response.read()
            token_start = reply.find('>opaquelocktoken:')
            token_end = reply.find('<', token_start)
            if token_start > 0 and token_end > 0:
                self.lock_token = reply[token_start+1:token_end]
                self.did_lock = 1
        else:
            # We can't lock her sir!
            if response.status == 423:
                message = '(object already locked)'
            else:
                message = ''

            if NSRunAlertPanel(response.read(),
                               'Lock request failed %s' % message,
                               'Retry', 'Cancel', None):
                self.lock()
            else:
                self.did_lock = 0
        return self.did_lock

    def unlock(self, interactive=1):
        """Remove webdav lock from edited zope object"""
        if not self.did_lock or self.lock_token is None:
            return 0 # nothing to do

        headers = {'Lock-Token':self.lock_token}
        response = self.zopeRequest('UNLOCK', headers)

        if interactive and response.status / 100 != 2:
            # Captain, she's still locked!
            if NSRunAlertPanel(response.read(),
                               'Unlock request failed',
                               'Retry', 'Cancel', None):
                self.unlock()
            else:
                self.did_lock = 0
        else:
            self.did_lock = 1
            self.lock_token = None
        return self.did_lock

    def zopeRequest(self, method, headers={}, body=''):
        """Send a request back to Zope"""
        try:
            if self.ssl:
                h = HTTPSConnection(self.host)
            else:
                h = HTTPConnection(self.host)

            h.putrequest(method, self.path)
            h.putheader('User-Agent', 'Zope External Editor/%s' % __version__)
            h.putheader('Connection', 'close')

            for header, value in headers.items():
                h.putheader(header, value)

            h.putheader("Content-Length", str(len(body)))

            if self.metadata.get('auth','').startswith('Basic'):
                h.putheader("Authorization", self.metadata['auth'])

            if self.metadata.get('cookie'):
                h.putheader("Cookie", self.metadata['cookie'])

            h.endheaders()
            h.send(body)
            return h.getresponse()
        except:
            # On error return a null response with error info
            class NullResponse:
                def getheader(self, n, d=None):
                    return d

                def read(self):
                    return '(No Response From Server)'

            response = NullResponse()
            response.reason = sys.exc_info()[1]

            try:
                response.status, response.reason = response.reason
            except ValueError:
                response.status = 0

            if response.reason == 'EOF occurred in violation of protocol':
                # Ignore this protocol error as a workaround for
                # broken ssl server implementations
                response.status = 200

            return response

    def __del__(self):
        """Let's clean up after ourselves, shall we?"""
        if self.lock_token:
            self.unlock(interactive=0)

        os.remove(self.getContentFile())
