##
## Name:    dnd.py
## Purpose: Interface to Dartmouth Name Directory services
## Author:  M. J. Fromberger <http://www.dartmouth.edu/~sting/>
## Info:    $Id: dnd.py 752 2007-01-09 03:20:37Z sting $
##
## Copyright (C) 2004-2007 Michael J. Fromberger, All Rights Reserved.
##
## Permission is hereby granted, free of charge, to any person
## obtaining a copy of this software and associated documentation
## files (the "Software"), to deal in the Software without
## restriction, including without limitation the rights to use, copy,
## modify, merge, publish, distribute, sublicense, and/or sell copies
## of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
## HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
## WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
## DEALINGS IN THE SOFTWARE.
##

import errno, os, socket, re, sys, weakref
from Crypto.Cipher import DES

__version__ = "1.7"

# Characters that are legal in name fields apart from letters/digits
nf_extras = "- ._\(\)&\+\*\"'"

# A regex matching a legal "name" query string
name_query_re = re.compile(r"^([A-Za-z0-9]|[%s])+$" % nf_extras)

# A regex matching a legal UID query
uid_query_re  = re.compile(r'#\d+$')

# A regex matching a legal DCTSNUM field query (Dartmouth only)
dcts_query_re = re.compile(r'\*(?:hd)?\d{5}[A-Z]$', re.IGNORECASE)

# {{ check_query_key(q)

def check_query_key(q):
    """Check whether the given query key q is valid as a DND query.
    Returns True or False.
    """
    return name_query_re.match(q) is not None or \
           uid_query_re.match(q) is not None  or \
           dcts_query_re.match(q) is not None

# }}

# {{ encrypt_challenge(rnd, key)

def encrypt_challenge(rnd, key):
    """Encrypt a random challenge from the DND using the user's key.

    rnd    -- Octal-encoded challenge from the DND (str)
    key    -- User's cleartext password (str)

    Note: Due to the limitations of the DND protocol, the user's key
    may be at most DES.key_size in length, i.e., 8 characters. 
    """
    rnd = decode_octal(rnd)
    
    if len(key) < DES.key_size:
        pad = chr(0) * (DES.key_size - len(key))
        key += pad
    
    dkey = DES.new(key, DES.MODE_ECB)
    result = dkey.encrypt(rnd); del(dkey)
    
    return encode_octal(result)

# }}

# {{ encrypt_change(old, new)

def encrypt_change(old, new):
    """Encrypt old and new passwords for a DND change password
    request.  Returns a tuple consisting of the old password encrypted
    using the new one as a key, and the new password encrypted using
    the old one as a key, both encoded as a string of ASCII octal
    digits as required by the DND protocol.

    old   -- Old cleartext password (str)
    new   -- New cleartext password (str)
    """
    if len(old) < DES.key_size:
        pad = chr(0) * (DES.key_size - len(old))
        old += pad
    
    if len(new) < DES.key_size:
        pad = chr(0) * (DES.key_size - len(new))
        new += pad
    
    okey = DES.new(old, DES.MODE_ECB)
    nkey = DES.new(new, DES.MODE_ECB)
    
    old_w_new = nkey.encrypt(old); del(nkey)
    new_w_old = okey.encrypt(new); del(okey)
    
    return (encode_octal(old_w_new), encode_octal(new_w_old))

# }}

# {{ encode_octal(s)

def encode_octal(s):
    """Encode the characters of an ASCII string as octal digits.  Each
    character is represented by a sequence of 3 consecutive octal
    digits representing its ASCII value.
    """
    return ''.join("%03o" % ord(v) for v in s)

# }}

# {{ decode_octal(s)

def decode_octal(s):
    """Decode a sequence of octal digits into a string.  Each block of
    three octal digits convey the value of a single ASCII character.
    The input is left-padded with zeroes if the length is not a
    multiple of three.
    """
    while len(s) % 3 <> 0:
        s = '0' + s
    
    return ''.join(chr(int(x, 8))
                   for x in (s[x : x + 3]
                             for x in xrange(0, len(s), 3)))

# }}

# {{ enquote_string(s)

def enquote_string(s):
    """Enquotes a value according to the DND protocol rules.  All
    interior quotation marks are doubled, and the resulting string is
    enclosed in double quotations.
    """
    return '"' + s.replace('"', '""') + '"'

# }}

# {{ dequote_string(s)

def dequote_string(s):
    """Removes quotation marks from a string according to the DND
    protocol rules.  Internal quotations ("") are replaced with single
    quotes, and the leading and trailing quotes are stripped.
    
    See also:  enquote_string()
    """
    if s.startswith('"'):
        s = s[1:]
    if s.endswith('"'):
        s = s[:-1]
    
    return s.replace('""', '"')

# }}

# {{ lookup(...)

def lookup(query, fields = (), **config):
    """This is a wrapper function that creates a DNDSession object and
    uses it to issue the specified query.

    query   -- the query to send to the DND (str).
    fields  -- a sequence of field names to look up.

    Additional keyword arguments are passed to the DNDSession
    constructor.
    """
    d = DNDSession(**config)
    try:
        return d.lookup(query, *fields)
    finally:
        d.close()

# }}

# {{ lookup_unique(...)

def lookup_unique(query, fields = (), **config):
    """This is a wrapper function that creates a DNDSession object and
    uses it to issue the specified query.

    query   -- the query to send to the DND (str).
    fields  -- a sequence of field names to look up.

    Additional keyword arguments are passed to the DNDSession
    constructor.
    """
    d = DNDSession(**config)
    try:
        return d.lookup_unique(query, *fields)
    finally:
        d.close()

# }}

# {{ class DNDError and subclasses

class DNDError ( Exception ):
    """The root class for DND errors."""

class DNDProtocolError (DNDError):
    """An exception representing protocol errors encountered during 
    interaction with a DND server.  The `key' field gives the numeric
    error code, the `value' field gives the descriptive text returned
    by the server.
    """
    def __init__(self, key, value=''):
        self.key = key
        self.value = value
    
    def __str__(self):
        return `self.value`

class DNDLostConnection (DNDError):
    pass

class DNDNotConnected (DNDError):
    pass

# }}

# {{ class DNDField

class DNDField (object):
    """Represents a field key in the DND.  Fields have permissions
    associated with them, determining who can read and write the
    contents of the field.  The general permission scheme is:

    A   -- anyone may do this operation (unauthenticated)
    U   -- the user whose record this is may do this operation
    N   -- nobody may perform this operation (administrator only)
    T   -- trusted users may perform this operation
    """
    _ptypes = {
        'all':   'A', 'any':     'A', 'everyone': 'A',
        'user':  'U', 'owner':   'U', 'self':     'U',
        'none':  'N', 'nobody':  'N', 'root':     'N',
        'trust': 'T', 'trusted': 'T', 'admin':    'T',
        'a': 'A', 'u': 'U', 'n': 'N', 't': 'T'}

    def __init__(self, name, rd, wr):
        """Initialize a new DNDField instance:

        name   -- the name of the field (str)
        rd     -- who has read access to the field (str)
        wr     -- who has write access to the field (str)
        """
        self._name  = name
        self._read  = self.permtype(rd)
        self._write = self.permtype(wr)

    def name(self): return self._name

    def read(self): return self._read

    def write(self): return self._write
    
    def is_readable(self, bywhom = 'any'):
        """Returns True if the field is readable by the specified
        category.  This may either be a string, or a sequence of
        strings; in the latter case, True is returned if at least one
        of the categories listed can read the field.  If the field is
        not readable, False is returned.
        """
        if isinstance(bywhom, basestring):
            return self.permtype(bywhom) == self._read
        else:
            for elt in bywhom:
                if self.permtype(elt) == self._read:
                    return True
            return False

    def is_writable(self, bywhom = 'user'):
        """Returns True if the field is writable by the specified
        category.  This may either be a string, or a sequence of
        strings; in the latter case, True is returned if at least one
        of the categories listed can write the field.  If the field is
        not writable, False is returned.
        """
        if isinstance(bywhom, basestring):
            return self.permtype(bywhom) == self._write
        else:
            for elt in bywhom:
                if self.permtype(elt) == self._write:
                    return True
            return False
    
    @staticmethod
    def permtype(key):
        """Map a string describing a category of permissions to the
        DND's corresponding permission letter.
        """
        try:
            return DNDField._ptypes[key.lower()]
        except KeyError:
            raise ValueError("Unknown permission category: %s" % key)

    def __repr__(self):
        return '#<%s %s read=%s write=%s>' % \
               (type(self).__name__,
                self._name, self._read, self._write)

    def __eq__(self, other):
        """Two DNDFields are equal if their names are equal without
        respect to case.  A DNDField is equal to a string if the
        string is equal to the name of the field.
        """
        try:
            self._name.lower() == other._name.lower()
        except AttributeError:
            return self._name.lower() == other.lower()

    def __hash__(self):
        return hash(self._name.lower())

# }}

# {{ class DNDRecord

class DNDRecord (dict):
    """This class represents a record in the DND.  It inherits from a
    dictionary, so you can use ordinary dictionary methods, but string
    keys are case-insensitive, and each key can be accessed as if it
    were an attribute as well, provided it is syntactically legal to
    do so (e.g., a field named "class" would not work).
    """
    def __init__(self, session, query, pw = None):
        self._session = weakref.ref(session)
        self._query = query
        self._pass = pw

    def __hash__(self):
        return hash(tuple(self.items()))
    
    def __getitem__(self, key):
        return super(DNDRecord, self).__getitem__(key.lower())
    
    def __setitem__(self, key, val):
        super(DNDRecord, self).__setitem__(key.lower(), val)

    def __contains__(self, key):
        return super(DNDRecord, self).__contains__(key.lower())
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("no such key: %s" % name)

# }}

# {{ class RecordSet

class RecordSet (set):
    """Abstraction of a set of records.  Basically, this is a set
    but it has a '.more' attribute that is set so that the user can
    tell whether the query from which this record set was generated
    had additional records that were not returned by the server.
    """
    def __init__(self, itms = ()):
        super(RecordSet, self).__init__(itms)
        self.more = False

# }}

# {{ class DNDSession

class DNDSession (object):
    """This class represents an open session with a DND server.
    """
    TRUST = ('TRUST',)  ## Magic token to indicated trust
    
    def __init__(self, **config):
        """Connect to the DND.  If the server and port are not
        specified, the hostname defaults to 'dnd' in the local domain,
        and the port to 902 which is the DND's default.
        
        The following keyword arguments may be used to configure other
        aspects of the session's behaviour:
        
        server         -- hostname of the DND server to contact.
        port           -- port number to contact on the DND server.
        debug          -- if true, diagnostics are written to stderr.
        default_fields -- a sequence of field keys for dict lookups.
        """
        server        = config.get('server')
        if server is None:
            server = os.getenv('DNDHOST', 'dnd')
        
        port          = config.get('port', 902)
        self._dfields = config.get('default_fields', ())
        self._debug   = config.get('debug', False)

        self._fcache  = None  # Cache of DNDField records
        self._saddr   = None  # Remote server (addr, port)
        self._conn    = None  # The socket object
        self._input   = None  # File stream associated with _conn

        try:
            self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._conn.connect((server, port))
        except socket.error, e:
            raise DNDError(str(e))

        self._saddr = self._conn.getpeername()
        self._input = self._conn.makefile()

        self._expect(220)

        self.set_default_fields(*config.get('default_fields', ()))

    def __repr__(self):
        base = '#<%s %s' % (type(self).__name__, id(self))
        if self.is_connected():
            return base + ' connected to %s port %s>' % self._saddr
        else:
            return base + ' disconnected>'
    
    def is_connected(self):
        """Returns True if the session is currently connected; False
        otherwise.
        """
        return self._conn is not None
    
    def close(self):
        """Send the QUIT command to the DND server, and close the session.
        """
        if self.is_connected():
            try:
                try:
                    self._cmd0("QUIT")
                    key, data = self._expect(200)
                    return key
                except DNDError:
                    pass
            finally:
                self._close()
        else:
            raise DNDNotConnected("session is not connected")
    
    def _close(self):
        """Low-level close method; shuts down the socket and fixes up
        the internal state variables.
        """
        try:
            self._conn.shutdown(2)
        except (socket.error, DNDError):
            pass

        self._conn  = None
        self._input = None
        self._saddr = None
    
    def fieldinfo(self, force = False):
        """Retrieve the set of fields available on the DND.  The
        result is cached the first time it is looked up, so that
        subsequent calls will return the stored value.
        
        To force a reload of the cache, pass force = True.

        This method returns a set of DNDField objects.
        """
        if self._fcache is None or force:
            self._cmd0("FIELDS")
            key, data = self._expect(102)

            fd = set()
            for i in xrange(int(data)):
                key, data = self._expect(120)
                name, wr, rd = data.split(' ')
                fd.add(DNDField(name.upper(), rd, wr))

            self._expect(200)
            self._fcache = fd

        return self._fcache

    def fieldnames(self, force = False):
        """Retrieve the set of field names available on the DND.  This
        is just a wrapper around .fieldinfo(), so the meaning of the
        force parameter and the caching semantics are the same.
        """
        return set(f.name() for f in self.fieldinfo(force))
    
    def field(self, name):
        """Return the information for a single field."""

        for elt in self.fieldinfo():
            if elt == name:
                return elt
        else:
            raise DNDError("no such field: %s" % name)

    def set_default_fields(self, *names):
        for elt in names:
            self.field(elt) # if this succeeds, we're happy

        self._dfields = names
    
    def readable_fields(self, bywhom='any'):
        """Return a set of the field names available on the DND which
        are readable by the specified category.
        """
        return set(elt.name() for elt in self.fieldinfo() if
                   elt.is_readable(bywhom))
    
    def writable_fields(self, bywhom='user'):
        """Return a set of the field names available on the DND which
        are writable by the specified category.
        """
        return set(elt.name() for elt in self.fieldinfo() if
                   elt.is_writable(bywhom))
    
    def keep_alive(self):
        """Send a NOOP command to the DND.  This prevents an idle
        session from being disconnected, but has no other effect.
        """
        self._cmd0("NOOP")
        self._expect(200)
    
    def lookup(self, query, *fields):
        """Look up the specified key in the DND.  If no query fields
        are specified, default query fields are used, if available.
        
        See also:  ._lookup()
        """
        if len(fields) == 0:
            return self._lookup(query, *self._dfields)
        else:
            return self._lookup(query, *fields)
    
    def _lookup(self, query, *fields):
        """This is the back end for all query operations.  If fields
        is empty, the number of matching records is returned (if any);
        else a RecordSet containing one DNDRecord for each matching
        record is returned.  The RecordSet has its "more" attribute
        set to True if the DND said there were additional matching
        records not given.

        query    -- the query string to issue
        fields   -- zero or more DND field names (strings)
        """
        if not check_query_key(query):
            raise DNDError('incorrectly formed query string: %s' % query)
        
        self._cmdq('LOOKUP', query, fields)
        key, data = self._expect(101)

        n_rec, n_fld = [int(x) for x in data.split(' ', 2)]
        if n_fld > 0:
            records = RecordSet()

            for rec in xrange(n_rec):
                elt = DNDRecord(self, query)

                for fld in xrange(n_fld):
                    key, data = self._expect(110)
                    elt[fields[fld]] = data

                records.add(elt)

            key, data = self._expect(200, 201)
            if key == 201:
                records.more = True
            
            return records
        else:
            self._expect(200, 201)
            return n_rec
    
    def lookup_unique(self, key, *fields):
        """Like lookup(...), but returns False if more than one match was
        found.  This permits you to easily look up a user for whom you
        want a unique match."""
        
        match = self.lookup(key, *fields)
        try:
            if len(match) == 1:
                return match.pop()
        except TypeError:
            if match == 1:
                return True
        
        return False
    
    def validate(self, query, pw, *fields):
        """Issues a validation query to the DND server.  If
        successful, a dictionary containing the requested fields is
        returned, or, if no fields were requested, 1 is returned.
        Raises a DNDProtocolError in case of an authentication
        failure.

        query   -- the query identifying the user to validate (str).
        pw      -- the user's cleartext password (str)
        fields  -- field names returned upon successful validation.
        """
        if len(fields) == 0:
            return self._validate(query, pw, *self._dfields)
        else:
            return self._validate(query, pw, *fields)
    
    def begin_validate(self, query, *fields):
        """Initiates a validation query to the DND server.  If
        successful, a tuple (c, r) is returned.  The value of "c" is
        the octal challenge string from the DND.  The value of "r" is
        a two-argument procedure to complete the validation:
        
        r(resp, True)   -- this is the encrypted response.
        r(pw, False)    -- this is the unencrypted password.
        
        If the unencrypted password is given, the original challenge
        is encrypted and sent; this is the default behaviour.
        """
        return self._begin_val(query, *fields)
    
    def _begin_val(self, query, *fields):
        self._cmdq("VALIDATE", query, fields)
        key, data = self._expect(300)
        
        def respond(pw, enc = False):
            if pw is DNDSession.TRUST:
                self._cmd0('TRUST')
            else:
                if enc:
                    self._cmd1('PASE', pw)
                else:
                    self._cmd1('PASE', encrypt_challenge(data, pw))
            
            key, val = self._expect(101)
            
            ignore, n_fld = val.split(' ', 2)
            output = DNDRecord(self, query, pw)
            for fld in xrange(int(n_fld)):
                key, val = self._expect(110)
                
                output[fields[fld]] = val
            
            self._expect(200)
            return (len(fields) == 0 and True) or output
        
        return data, respond
    
    def _validate(self, query, pw, *fields):
        data, respond = self._begin_val(query, *fields)
        return respond(pw)
    
    def enable_privs(self, query, pw):
        """Enable administrative privileges for this connexion.  Requires
        that the specified user have the AUTH, DBA, or TRUST permission in
        the PERM field of the DND.  May not be implemented for all DND's.
        
        Once this has been done, you can pass DNDSession.TRUST as the
        value of the password arguments for commands that otherwise
        would require a password.
        """
        if not check_query(query):
            raise DNDError('incorrectly formed query string: %s' % query)
        
        self._cmd1('PRIV', query)
        key, data = self._expect(300)
        self._cmd1('PASE', encrypt_challenge(data, pw))
        self._expect(200)
    
    def disable_privs(self):
        """Disable administrative privileges for this connexion."""
        self._cmd0('UNPRIV')
        self._expect(200)

    def add_record(self, record):
        """Add a new record to the DND.  The record information is
        given as a dictionary with field names as keys and field
        contents as values.

        This method requires that privileges be enabled.  
        """
        if not isinstance(record, dict):
            raise TypeError("new record must be a dictionary")
        
        keys = record.keys()
        self._cmd1('ADD', ' '.join(keys))
        self._expect(300)
        
        for key in keys:
            self._cmd0(record[key])

        self._expect(200)
    
    def change_record(self, user, pw, *fields):
        """Change one or more field values.  Each field value must be given
        as a tuple of (field-name, new-value), each value in a string.  The
        user given must have permission to change each field, or an error
        will result."""
        
        query = ""
        for q in fields:
            if type(q) <> tuple or len(q) <> 2:
                raise ValueError("Field changes must be of the form "
                                 "(field, value)")
            
            k = q[0] + " " + enquote_string(q[1])
            query += " " + k
        
        if not query:
            raise ValueError("You must specify at least one field to change.")
        
        self._cmd2("CHANGE", user, query[1:])
        key, data = self._expect(300)

        if pw is DNDSession.TRUST:
            self._cmd0("TRUST")
        else:
            self._cmd1("PASE", encrypt_challenge(data, pw))
        
        key, data = self._expect(200)
        return key
    
    def group_list(self, group, pw, *fields):
        """For each user in the specified group, return a record of the given
        fields.  If no fields are specified, only the number of matching users
        is returned."""
        
        self._cmdq("GROUP", group, fields)
        key, data = self._expect(300)

        if pw is DNDSession.TRUST:
            self._cmd0("TRUST")
        else:
            self._cmd1("PASE", encrypt_challenge(data, pw))
        
        key, data = self._expect(200, 110)
        
        matches = []
        while key == 110:
            matches.append(data)

            key, data = self._expect(200, 110)
        
        if len(fields) == 0:
            return len(matches)
        
        num_recs = len(matches) / len(fields)
        out = RecordSet(); pos = 0
        for rec in xrange(num_recs):
            item = DNDRecord(self, group)
            
            for fld in xrange(len(fields)):
                item[fields[fld]] = matches[pos]
                pos += 1
            
            out.add(item)
        
        return out
    
    def group_add(self, user, group, pw):
        """Add the specified user to the specified group."""
        
        self._cmd2("GROUPADD", user, group)
        key, data = self._expect(300)
        
        if pw is DNDSession.TRUST:
            self._cmd0("TRUST")
        else:
            self._cmd1("PASE", encrypt_challenge(data, pw))
        
        key, data = self._expect(200)
        return key
    
    def group_remove(self, user, group, pw):
        """Remove the specified user from the specified group."""
        
        self._cmd2("GROUPDEL", user, group)
        key, data = self._expect(300)
        
        if pw is DNDSession.TRUST:
            self._cmd0("TRUST")
        else:
            self._cmd1("PASE", encrypt_challenge(data, pw))
        
        key, data = self._expect(200)
        return key
    
    def change_pw(self, who, old, new):
        """Change the password for the specified user, given the user
        name, old password, and new password.  Returns True if this
        succeeds.
        """
        old_with_new, new_with_old = encrypt_change(old, new)
        self._cmd3("CHPW", who, old_with_new, new_with_old)
        self._expect(200)
        
        return True
    
    def hostname(self):
        """Return the hostname of the DND server."""
        if not self.is_connected():
            raise DNDNotConnected("session is not connected")

        return socket.gethostbyaddr(self._saddr[0])[0]
    
    def _diag(self, msg, *args):
        if self._debug:
            sys.stderr.write(msg % args)

    def _rawsend(self, data):
        """[private] Write directly to the low-level connection.  This
        method will detect if the connection is lost during the write.
        """
        if not self.is_connected():
            raise DNDNotConnected("session is not connected")

        try:
            self._conn.send(data)
        except socket.error, e:
            if e[0] == errno.EPIPE:
                self._close()
                raise DNDLostConnection("broken pipe")
            else:
                raise

    def __contains__(self, query):
        """Returns True if the specified object matches one or more
        records in the DND.  Returns False if the object is not a
        string, does not conform to the syntax for DND queries, or was
        not found in the DND.
        """
        if not isinstance(query, basestring) or not check_query_key(query):
            return False

        try:
            return self._lookup(query) > 0
        except DNDError, e:
            return False

    def __getitem__(self, query):
        """self[other] is equivalent to self.lookup_unique(other)"""
        return self.lookup_unique(query)
    
    def _readline(self):
        """[private] Read and parse a response line from the DND.
        Returns a tuple of (code, data), or raises an exception.
        """
        try:
            line = self._input.readline()
        except socket.error, e:
            if e[0] == errno.ECONNRESET:
                self._close()
                raise DNDLostConnection("connection closed by remote host")
            else:
                raise
        except AttributeError:
            raise DNDNotConnected("session is not connected")

        if line == '':
            self._close()
            raise DNDLostConnection("connection closed by remote host")

        # Careful not to strip before splitting, as some fields are empty
        key, data = line.split(' ', 1)
        key = int(key) ; data = data.rstrip()
        self._diag('>> [%03d] %s\n', key, data)
        
        return key, data
    
    def _cmd0(self, cmd):
        msg = cmd + "\n"
        self._diag('<< %s', msg)
        self._rawsend(msg)
    
    def _cmd1(self, cmd, arg):
        msg = cmd + " " + arg + "\n"
        self._diag('<< %s', msg)
        self._rawsend(msg)
    
    def _cmd2(self, cmd, arg1, arg2):
        msg = cmd + " " + arg1 + "," + arg2 + "\n"
        self._diag('<< %s', msg)
        self._rawsend(msg)
    
    def _cmd3(self, cmd, arg1, arg2, arg3):
        msg = cmd + " " + ','.join((arg1, arg2, arg3)) + "\n"
        self._diag('<< %s', msg)
        self._rawsend(msg)
    
    def _cmdq(self, cmd, key, qargs):
        msg = '%s %s' % (cmd, key)
        if qargs:
            msg += ','
            msg += ' '.join(qargs)

        msg += '\n'
        self._diag('<< %s', msg)
        self._rawsend(msg)
    
    def _expect(self, *wanted):
        out = key, data = self._readline()
        
        if key not in wanted:
            raise DNDProtocolError(key, data)
        else:
            return out

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self._diag('[disposing of %s]\n', self)
            self.close()
        except:
            pass
    
    def __del__(self):
        """Insures that the .close() method is called when the object
        is reclaimed by the memory management system.  Exceptions that
        result from the call to .close() are ignored.
        """
        try:
            self._diag('[disposing of %s]\n', self)
            self.close()
        except:
            pass    

# }}

_tvar_re = re.compile(r'%([<>]?=?\d+)?\((#?\w+)'
                      r'([?/](?:[^\\()]|\\[\\()])+)?\)',
                      re.DOTALL)

# {{ format_fields(template, entry)

def format_fields(template, entry, trunc_mark = ' ...'):
    """Given a string template and a dictionary mapping field names to
    values, return the string that results from substituting field
    values for named template variables.
    
    A template variable has one of the following formats:
    
    %(field)       -- field value, error if field is not defined.
    %(field?alt)   -- field value, literal alt text if not defined.
    %(field/alt)   -- field value, literal alt text if field is empty.
    
    A field name may optionally be prefixed with an alignment
    specifier and a minimum field width, as in these examples:
    
    %<20(field)    -- left-justified field, at least 20 characters
    %>10(field)    -- right-justified field, at least 10 characters
    %=15(field)    -- left-justified field, exactly 15 characters
    %>=15(field)   -- right-justified field, exactly 15 characters
    
    Fields are padded with space characters."""
    
    out = '' ; last_end = 0
    for match in _tvar_re.finditer(template):
        out += template[last_end : match.start()]
        
        main_len = match.group(1)
        main_key = match.group(2)
        alt_key  = match.group(3)
        
        if main_key in entry:
            sub_data = entry[main_key].strip()
            
            if not sub_data and alt_key and alt_key.startswith('/'):
                sub_data = alt_key[1:] . \
                           replace('\(', '(') . \
                           replace('\)', ')') . \
                           replace('\\\\', '\\')
        elif alt_key and alt_key.startswith('?'):
            sub_data = alt_key[1:] . \
                       replace('\(', '(') . \
                       replace('\)', ')') . \
                       replace('\\\\', '\\')
        else:
            raise KeyError("No field named '%s' defined in entry" %
                           main_key)
        
        trunc = None ; format = "%s"
        if main_len:
            real_len = int(main_len.lstrip('<>='))

            if main_len[0] in ('<', '>'):
                if main_len[0] == '<':
                    real_len *= -1
                main_len = main_len[1:]

            if main_len.startswith('='):
                trunc = abs(real_len)

            format = "%%%ds" % real_len
        
        if trunc:
            if len(sub_data) > trunc and \
               trunc > len(trunc_mark):
                sub_data = sub_data[:trunc - len(trunc_mark)] + trunc_mark
            else:
                sub_data = sub_data[:trunc]
        
        out += (format % sub_data)
        last_end = match.end()
    
    out += template[last_end:]
    
    return out

# }}

# {{ get_format_fields(s)

def get_format_fields(s):
    """Return a list of the names of all the query fields specified in
    the given format string."""
    
    out = set()
    for match in _tvar_re.finditer(s):
        if match.group(2)[0] <> '#':
            out.add(match.group(2))
        
        alt = match.group(3)
        if alt and alt[0] == '?':
            out.add(alt[1:])
    
    return list(out)

# }}

__all__ = ('DNDSession', 'RecordSet', 'DNDRecord', 'DNDField',
           'DNDError', 'DNDProtocolError', 'DNDLostConnection',
           'DNDNotConnected',
           'lookup', 'lookup_unique',
           'enquote_string', 'dequote_string',
           'encode_octal', 'decode_octal',
           'encrypt_challenge', 'encrypt_change',
           'check_query_key',
           'format_fields', 'get_format_fields',
           )

# Here there be dragons
