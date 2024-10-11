#!/bin/env python3.7

import os
import sys

if __name__ == "__main__":

  count = 1

  root = os.getcwd()

  checks = list()

  for i in range( 1, len( sys.argv ) ):
    checks.append( sys.argv[ i ] )

  write = open( "wesign.summary", "w" )

  for check in checks:

    if os.path.exists( check ):
      read = open( check, "r" )

      for line in read.readlines():
        write.write( str( count ) + ", " + line )
        count += 1

      read.close()

  write.close()

  sys.exit( 0 )
