#!/usr/bin/env python
# encoding: utf-8
"""
spccalc.py

Created by Philippe Langlois on 2009-11-18.
Copyright (c) 2009 P1 Security. All rights reserved.

Code under eGPL license. http://www.egpl.info
"""

import sys
import getopt


help_message = '''
SS7calc - SS7 Signaling Point Code calculator

"-h", "--help"
	displays this message
"-3", "--383"
	set Signaling Point Code as 3-8-3 Format
"-5", "--545"
   set Signaling Point Code as 5-4-5 Format
"-i", "--int"
	set Signaling Point Code as decimal format
"-u", "--itu"
	specify SPC as ITU
"-a", "--ansi"
	specify SPC as ANSI


Format: 5-4-5
>>> 30*2**9 + 0*2**5 + 30
15390

>>> pc="30-0-30"
>>> int(pc.split('-')[0]) * 2**9 + int(pc.split('-')[1]) * 2**5 + int(pc.split('-')[2])
15390

>>> pc=15390
>>> ('-').join( ("%d"%(pc >> 9), "%d"%((pc- a*2**9) >> 5), "%d"%(pc - a*2**9 - b*2**5)) )
'30-0-30'

For more information:
http://en.wikipedia.org/wiki/Point_code

For online versions:
http://jhartman.webd.pl/pc/index.php
http://www.linuxfocus.org/~guido/javascript/ansi-point-code-converter.htm
'''

class SPC():
   def __init__(self, intv = None):
      self.spc = None
      self.verbose = False
      self.kind = None
      
   def set_int(self, intv):
      if self.verbose: print "Setting spc=%s" % intv
      self.spc = int(intv)
      
   def set_itu(self):
      self.kind = "ITU"
      self.kind_detail = "14 bits"
   
   def set_ansi(self):
      self.kind = "ANSI"
      self.kind_detail = "24 bits"
      
   def kind_string(self):
      if self.kind is None:
         return "Unknown"
      else:
         return "%s (%s)" % (self.kind.upper(), self.kind_detail)

   def check_split(self, s):
      l = s.split('-')
      if len(l) is not 3:
         print "Error: Wrong format, should be like A-B-C"
         return None, None, None
      else:
         a, b, c = l
         if self.verbose: print "%s --> %d-%d-%d" % (s, a, b, c)
         return a, b, c
      
   def set_545(self, spc545):
      l = spc545.split('-')
      if len(l) is not 3:
         print "Error: Wrong format, should be like A-B-C"
         return
      else:
         a, b, c = l
         a = int(a)
         b = int(b)
         c = int(c)
         if a > 2**5 or b > 2**4 or c > 2**5:
            print "Error: %s does not look like Signaling Point Code Format 5-4-5 (max=%d-%d-%d, min=0-0-0), maybe it is ANSI (8-8-8)?\n" % (spc545, 2**5, 2**4, 2**5)
            return
         self.spc = a*2**9 + b*2**5 + c

   def set_383(self, s):
      a, b, c = self.check_split(s)
      if a is not None:
         a = int(a)
         b = int(b)
         c = int(c)
         if a > 2**3 or b > 2**8 or c > 2**3:
            print "Error: %s does not look like Signaling Point Code Format 3-8-3 (max=%d-%d-%d, min=0-0-0), maybe it is ANSI (8-8-8)?\n" % (s, 2**3, 2**8, 2**3)
            return
         self.spc = a*2**11 + b*2**3 + c
      
   def to_545(self):
      pc = int(self.spc)
      a = pc >> 9
      b = (pc- a*2**9) >> 5
      c = pc - a*2**9 - b*2**5
      return ('-').join( ("%d"%a, "%d"%b, "%d"%c) )

   def to_383(self):
      pc = int(self.spc)
      a = pc >> 11
      b = (pc- a*2**11) >> 3
      c = pc - a*2**11 - b*2**3
      return ('-').join( ("%d"%a, "%d"%b, "%d"%c) )

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
   if argv is None:
   	argv = sys.argv
   try:
      try:
      	opts, args = getopt.getopt(argv[1:], "ho:vi:3:5:ua", ["help", "output=", "int=", "383=", "545=", "itu", "ansi"])
      except getopt.error, msg:
      	raise Usage(msg)

      spc = SPC()
      # option processing
      for option, value in opts:
      	if option == "-v":
      		verbose = True
      		spc.verbose = True
      	#
      	if option in ("-h", "--help"):
      		raise Usage(help_message)
      	# 
      	if option in ("-o", "--output"):
      		output = value
      	#
      	if option in ("-3", "--383"):
      		spc.set_383(value)
      		spc.set_itu()
      	#
      	if option in ("-5", "--545"):
      		spc.set_545(value)
      		spc.set_itu()
      	# 
      	if option in ("-u", "--itu"):
      		spc.set_itu()
      		
      	if option in ("-a", "--ansi"):
      		spc.set_ansi()
      		
      	if option in ("-i", "--int"):
      		spc.set_int(value)


      
      if spc.spc is not None:
         print "SS7calc - SS7 Signaling Point Code calculator\n"
         print "SPC Decimal : %d" % spc.spc
         print "Format      : %s" % spc.kind_string()
         print "5-4-5 Format: " + spc.to_545()
         print "3-8-3 Format: " + spc.to_383()
      else:
         print "Error: Please set a value for PC\n"
         print help_message

   except Usage, err:
   	print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
   	print >> sys.stderr, "\t for help use --help"
   	return 2


if __name__ == "__main__":
	sys.exit(main())
