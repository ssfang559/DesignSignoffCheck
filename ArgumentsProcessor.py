#!/bin/env python3.7

import re
import sys

class ArgumentsProcessor:

  def __init__( self ):

    name = ""

    self.arguments = dict()

    for argv in sys.argv:

      if re.match( r'^-', argv ):

        name = re.sub( r'^-', "", argv )

        self.arguments[ name ] = list()

      else:

        if name != "":

          self.arguments[ name ].append( argv )

  def get( self ):

    return self.arguments

if __name__ == "__main__":

  arguments = ArgumentsProcessor()

  print( arguments.get() )
#!/bin/env python3.7

import re
import sys

class ArgumentsProcessor:

  def __init__( self ):

    name = ""

    self.arguments = dict()

    for argv in sys.argv:

      if re.match( r'^-', argv ):

        name = re.sub( r'^-', "", argv )

        self.arguments[ name ] = list()

      else:

        if name != "":

          self.arguments[ name ].append( argv )

  def get( self ):

    return self.arguments

if __name__ == "__main__":

  arguments = ArgumentsProcessor()

  print( arguments.get() )
