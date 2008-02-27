# $Id$

# Copyright (C) 2007--2008  American Registry for Internet Numbers ("ARIN")
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND ARIN DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS.  IN NO EVENT SHALL ARIN BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

"""SAX utilities."""

import xml.sax, lxml.sax

class handler(xml.sax.handler.ContentHandler):
  """SAX handler for RPKI protocols.

  This class provides some basic amenities for parsing protocol XML of
  the kind we use in the RPKI protocols, including whacking all the
  protocol element text into US-ASCII, simplifying accumulation of
  text fields, and hiding some of the fun relating to XML namespaces.

  General assumption: by the time this parsing code gets invoked, the
  XML has already passed RelaxNG validation, so we only have to check
  for errors that the schema can't catch, and we don't have to play as
  many XML namespace games.
  """

  def __init__(self):
    """Initialize SAX handler."""
    self.text = ""
    self.stack = []

  def startElementNS(self, name, qname, attrs):
    """Redirect startElementNS() events to startElement()."""
    return self.startElement(name[1], attrs)

  def endElementNS(self, name, qname):
    """Redirect endElementNS() events to endElement()."""
    return self.endElement(name[1])

  def characters(self, content):
    """Accumulate a chuck of element content (text)."""
    self.text += content

  def startElement(self, name, attrs):
    """Handle startElement() events.

    We maintain a stack of nested elements under construction so that
    we can feed events directly to the current element rather than
    having to pass them through all the nesting elements.

    If the stack is empty, this event is for the outermost element, so
    we call a virtual method to create the corresponding object and
    that's the object we'll be returning as our final result.
    """
    a = dict()
    for k,v in attrs.items():
      if isinstance(k, tuple):
        if k == ("http://www.w3.org/XML/1998/namespace", "lang"):
          k = "xml:lang"
        else:
          assert k[0] is None
          k = k[1]
      a[k.encode("ascii")] = v.encode("ascii")
    if len(self.stack) == 0:
      assert not hasattr(self, "result")
      self.result = self.create_top_level(name, a)
      self.stack.append(self.result)
    self.stack[-1].startElement(self.stack, name, a)

  def endElement(self, name):
    """Handle endElement() events.

    Mostly this means handling any accumulated element text.
    """
    text = self.text.encode("ascii").strip()
    self.text = ""
    self.stack[-1].endElement(self.stack, name, text)

  @classmethod
  def saxify(cls, elt):
    """Create a one-off SAX parser, parse an ETree, return the result.
    """
    self = cls()
    lxml.sax.saxify(elt, self)
    return self.result
