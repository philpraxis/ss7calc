#!/usr/bin/env python
# encoding: utf-8
"""
ss7calc.py

Created by Philippe Langlois on 2009-11-18.
Copyright (c) 2009 P1 Security. All rights reserved.
http://www.p1security.com

Code under eGPL license. http://www.egpl.info
"""
import sys
import getopt
import os

help_message = '''Usage:
"-h", "--help"
	displays this message
"-3", "--383"
	set Signaling Point Code as 3-8-3 Format (Recommended, used by ITU)
"-5", "--545"
   set Signaling Point Code as 5-4-5 Format
"-i", "--int"
	set Signaling Point Code as decimal format
"-u", "--itu"
	specify SPC as ITU
"-a", "--ansi"
	specify SPC as ANSI
"-r", "--read"
   pass file (or standard input if file is '-') and process the content as SPC values

Examples:
$ ./ss7calc.py -i 12345
SS7calc - SS7 Signaling Point Code calculator

SPC Decimal : 12345
Format      : Unknown
5-4-5 Format: 24-1-25
3-8-3 Format: 6-7-1

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
      self.csv = False
      
   def set_int(self, intv):
      if self.verbose: print(("Setting spc=%s" % intv))
      self.spc = int(intv)
      
   def set_itu(self):
      self.kind = "ITU"
      self.kind_detail = "14 bits"
   
   def set_ansi(self):
      self.kind = "ANSI"
      self.kind_detail = "24 bits"
      
   def set_display_csv(self):
      self.csv = True
      
   def kind_string(self):
      if self.kind is None:
         return "Unknown"
      else:
         return "%s (%s)" % (self.kind.upper(), self.kind_detail)

   def check_split(self, s):
      l = s.split('-')
      if len(l) is not 3:
         print("Error: Wrong format, should be like A-B-C")
         return None, None, None
      else:
         a, b, c = l
         if self.verbose: print(("%s --> %d-%d-%d" % (s, a, b, c)))
         return a, b, c

   def set_545(self, spc545):
      """
      >>> s = SPC()
      >>> s.set_545('1-2-3')
      >>> s.spc
      579
      >>>
      """
      l = spc545.split('-')
      if len(l) is not 3:
         print("Error: Wrong format, should be like A-B-C")
         return
      else:
         a, b, c = l
         a = int(a)
         b = int(b)
         c = int(c)
         if a > 2**5 or b > 2**4 or c > 2**5:
            print(("Error: %s does not look like Signaling Point Code Format 5-4-5 (max=%d-%d-%d, min=0-0-0), maybe it is ANSI (8-8-8)?\n" % (spc545, 2**5, 2**4, 2**5)))
            return
         self.spc = a*2**9 + b*2**5 + c

   def set_383(self, s):
      """
      >>> s = SPC()
      >>> s.set_383('1-2-3')
      >>> s.spc
      2067
      >>>
      """
      a, b, c = self.check_split(s)
      if a is not None:
         a = int(a)
         b = int(b)
         c = int(c)
         if a > 2**3 or b > 2**8 or c > 2**3:
            print(("Error: %s does not look like Signaling Point Code Format 3-8-3 (max=%d-%d-%d, min=0-0-0), maybe it is ANSI (8-8-8)?\n" % (s, 2**3, 2**8, 2**3)))
            return
         self.spc = a*2**11 + b*2**3 + c

   def get_545(self):
      pc = int(self.spc)
      a = pc >> 9
      b = (pc- a*2**9) >> 5
      c = pc - a*2**9 - b*2**5
      return a, b, c
      
   def to_545(self):
      """
      from ss7calc import *
      >>> s = SPC()
      >>> s.set_int(1234)
      >>> s.to_545()
      '2-6-18'
      >>>
      """
      a, b, c = self.get_545()
      return "%d-%d-%d"%(a,b,c)
      # return ('-').join( ("%d"%a, "%d"%b, "%d"%c) )

   def get_383(self):
      pc = int(self.spc)
      a = pc >> 11
      b = (pc- a*2**11) >> 3
      c = pc - a*2**11 - b*2**3
      return a, b, c

   def to_383(self):
      """
      >>> s = SPC()
      >>> s.set_int(1234)
      >>> s.to_383()
      '0-154-2'
      >>>
      """
      a, b, c = self.get_383()
      return "%d-%d-%d"%(a,b,c)
      # return ('-').join( ("%d"%a, "%d"%b, "%d"%c) )

   def display(self):
      """
      from ss7calc import *
      >>> s = SPC()
      >>> s.set_int(1234)
      >>> s.display()
      SPC Decimal : 1234
      Format      : Unknown
      5-4-5 Format: 2-6-18
      3-8-3 Format: 0-154-2
      <BLANKLINE>
      >>>
      """
      if self.csv is True:
         print(("%d,%s,%s,%s" % (self.spc, self.kind_string(), self.to_545(), self.to_383())))
      else:
         print(("SPC Decimal : %d" % self.spc))
         print(("Format      : %s" % self.kind_string()))
         print(("5-4-5 Format: " + self.to_545()))
         print(("3-8-3 Format: " + self.to_383()))
         print("")
         
   def header(self):
      """
      Displays header...
      """
      if self.csv is True:
         return "SS7calc,SS7 Signaling Point Code calculator,by Philippe Langlois,http://www.p1security.com\nSPC Decimal,Format,5-4-5 Format,3-8-3 Format"
      else:
         return "SS7calc - SS7 Signaling Point Code calculator\nby Philippe Langlois - http://www.p1security.com\n"

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
   read_file = None
   if argv is None:
   	argv = sys.argv
   try:
      try:
      	opts, args = getopt.getopt(argv[1:], "ho:vi:3:5:uar:c", ["help", "output=", "int=", "383=", "545=", "itu", "ansi", "read=", "csv"])
      except getopt.error as msg:
      	raise Usage(msg)

      spc = SPC()
      # option processing
      for option, value in opts:
      	if option == "-v":
      		verbose = True
      		spc.verbose = True
      	#
      	if option in ("-h", "--help"):
      	   print((spc.header()))
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
      		
      	if option in ("-r", "--read"):
      	   read_file = value
      	   
      	if option in ("-c", "--csv"):
      	   spc.set_display_csv()
      	   
      print((spc.header()))
      if read_file is not None:
         if read_file == "-":
            content = sys.stdin.readlines()
         else:
            content = open(read_file).readlines()
         s = spc
         for index,line in enumerate(content):
            s.set_int(line.strip())
            s.display()
         sys.exit()
      
      if spc.spc is not None:
         spc.display()
      else:
         print("Error: Please set a value for PC\n")
         print(help_message)

   except Usage as err:
   	print(sys.argv[0].split("/")[-1] + ": " + str(err.msg))
   	print("\t for help use --help")
   	return 2

if os.getenv("DOCTEST") == "1":
   """
   Hurra for doctest:
   DOCTEST=1 ./ss7calc.py -v
   http://docs.python.org/library/doctest.html

   But check this too:
   http://pycheesecake.org/wiki/PythonTestingToolsTaxonomy
   """
   import doctest
   sys.exit(doctest.testmod())

if __name__ == "__main__":
	sys.exit(main())
