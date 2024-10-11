#!/bin/env python3.7

import re
import sys

class ProjectInfo():

  def __init__( self ):

    self.projects = dict()

    self.projects[ "drjoa" ] = dict()

    self.project = "drjoa"
    self.process = "cxmt10G4"
    self.projects[ "drjoa" ][ "process" ] = "cxmt10G4"
    self.projects[ "drjoa" ][ "metalScheme" ] = "1p4m1x2y1z"
    self.projects[ "drjoa" ][ "cdsLib" ] = "/proj/drjoa/__VERSION__/libs/cds.lib"
    self.projects[ "drjoa" ][ "incFile" ] = "/apps/imctf/runset/calibre/cxmt10G4/current/common/empty_device.spi"
    self.projects[ "drjoa" ][ "simrc" ] = "/proj/drjoa/__VERSION__/setup/.simrc"

    self.projects[ "drpoa" ] = dict()

    self.project = "drpoa"
    self.process = "cxmt10G3"
    self.projects[ "drpoa" ][ "process" ] = "cxmt10G3"
    self.projects[ "drpoa" ][ "metalScheme" ] = "1p4m1x2y1z"
    self.projects[ "drpoa" ][ "cdsLib" ] = "/proj/drpoa/__VERSION__/libs/cds.lib"
    self.projects[ "drpoa" ][ "incFile" ] = "/apps/imctf/runset/calibre/cxmt10G3/current/common/empty_device.spi"
    self.projects[ "drpoa" ][ "simrc" ] = "/proj/drpoa/__VERSION__/setup/.simrc"

    self.projects[ "dqcop" ] = dict()

    self.project = "dqcop"
    self.projects[ "dqcop" ][ "process" ] = "cxmt10G5"
    self.projects[ "dqcop" ][ "metalScheme" ] = "1p4m1x2y1z"
    self.projects[ "dqcop" ][ "cdsLib" ] = "/proj/dqcop/__VERSION__/libs/cds.lib"
    self.projects[ "dqcop" ][ "incFile" ] = "/apps/imctf/runset/calibre/cxmt10G5/current/common/empty_device.spi"
    self.projects[ "dqcop" ][ "simrc" ] = "/proj/dqcop/__VERSION__/setup/.simrc"

    self.projects[ "drcot" ] = dict()

    self.project = "drcot"
    self.projects[ "drcot" ][ "process" ] = "cxmt10G5plus"
    self.projects[ "drcot" ][ "metalScheme" ] = "1p5m1x3y1z"
    self.projects[ "drcot" ][ "cdsLib" ] = "/proj/drcot/__VERSION__/libs/cds.lib"
    self.projects[ "drcot" ][ "incFile" ] = "/apps/imctf/runset/calibre/cxmt10G5plus/current/common/empty_device.spi"
    self.projects[ "drcot" ][ "simrc" ] = "/proj/drcot/__VERSION__/setup/.simrc"

    self.projects[ "droop" ] = dict()

    self.project = "droop"
    self.projects[ "droop" ][ "process" ] = "cxmt10G6"
    self.projects[ "droop" ][ "metalScheme" ] = "1p5m1x3y1z"
    self.projects[ "droop" ][ "cdsLib" ] = "/proj/droop/__VERSION__/libs/cds.lib"
    self.projects[ "droop" ][ "incFile" ] = "/apps/imctf/runset/calibre/cxmt10G6/current/common/empty_device.spi"
    self.projects[ "droop" ][ "simrc" ] = "/proj/droop/__VERSION__/setup/.simrc"

    self.projects[ "drpot" ] = dict()

    self.project = "drpot"
    self.projects[ "drpot" ][ "process" ] = "cxmt10G3"
    self.projects[ "drpot" ][ "metalScheme" ] = "1p4m1x2y1z"
    self.projects[ "drpot" ][ "cdsLib" ] = "/proj/drpot/__VERSION__/libs/cds.lib"
    self.projects[ "drpot" ][ "incFile" ] = "/apps/imctf/runset/calibre/cxmt10G3/current/common/empty_device.spi"
    self.projects[ "drpot" ][ "simrc" ] = "/proj/drpot/__VERSION__/setup/.simrc"

    self.projects[ "dqpoa" ] = dict()

    self.project = "dqpoa"
    self.projects[ "dqpoa" ][ "process" ] = "cxmt10G3"
    self.projects[ "dqpoa" ][ "metalScheme" ] = "1p4m1x2y1z"
    self.projects[ "dqpoa" ][ "cdsLib" ] = "/proj/dqpoa/__VERSION__/libs/cds.lib"
    self.projects[ "dqpoa" ][ "incFile" ] = "/apps/imctf/cad/runset/dqpoa/v5/current/empty_device.spi"
    self.projects[ "dqpoa" ][ "simrc" ] = "/proj/dqpoa/__VERSION__/setup/.simrc"

    self.projects[ "dqpmb" ] = dict()

    self.project = "dqpmb"
    self.projects[ "dqpmb" ][ "process" ] = "cxmt10G3"
    self.projects[ "dqpmb" ][ "metalScheme" ] = "1p4m1x2y1z"
    self.projects[ "dqpmb" ][ "cdsLib" ] = "/proj/" + self.project + "/__VERSION__/libs/cds.lib"
    self.projects[ "dqpmb" ][ "incFile" ] = "/apps/imctf/runset/calibre/" + self.process + "/current/common/empty_device.spi"
    self.projects[ "dqpmb" ][ "simrc" ] = "/proj/" + self.project + "/__VERSION__/setup/.simrc"

    self.projects[ "dqrmb" ] = dict()

    self.project = "dqrmb"
    self.process = "imc19n_RW"
    self.projects[ "dqrmb" ][ "process" ] = "imc19n_RW"
    self.projects[ "dqrmb" ][ "metalScheme" ] = "1p3m1x1y1z"
    self.projects[ "dqrmb" ][ "cdsLib" ] = "/proj/dqrmb/__VERSION__/libs/cds.lib"
    self.projects[ "dqrmb" ][ "incFile" ] = "/apps/imctf/runset/calibre/imc19n_RW/current/common/empty_device.spi"
    self.projects[ "dqrmb" ][ "simrc" ] = "/proj/dqrmb/__VERSION__/setup/.simrc"

    self.projects[ "dqrmt" ] = dict()

    self.project = "dqrmt"
    self.projects[ "dqrmt" ][ "process" ] = "imc19n_RW"
    self.projects[ "dqrmt" ][ "metalScheme" ] = "1p3m1x1y1z"
    self.projects[ "dqrmt" ][ "cdsLib" ] = "/proj/dqrmt/__VERSION__/libs/cds.lib"
    self.projects[ "dqrmt" ][ "incFile" ] = "/apps/imctf/runset/calibre/imc19n_RW/current/common/empty_device.spi"
    self.projects[ "dqrmt" ][ "simrc" ] = "/proj/dqrmt/__VERSION__/setup/.simrc"
    

  def get( self, project, version="" ):

    project = project.lower()

    if project in self.projects.keys():
      if version == "":
        if project == "dqrmb":
          version = "V4_TM"
        elif project == "dqpoa":
          version = "V5"
        elif project == "dqcop":
          version = "PV"
        elif project == "drcot":
          version = "TV"
        elif project == "drpot":
          version = "TV"
        elif project == "drpoa":
          version = "V0"
        elif project == "dqpmb":
          version = "V0"
        elif project == "drjoa":
          version = "V0"
        elif project == "droop":
          version = "PV"

      for key in self.projects[ project ].keys():
        self.projects[ project ][ key ] = re.sub( "__VERSION__", version, self.projects[ project ][ key ] )

      return self.projects[ project ]

    else:
      return None

if __name__ == "__main__":
  project = ProjectInfo()

  print( project.get( "dqpoa", "V5" ) )
  print( project.get( "DQPOA", "V0" ) )
  print( project.get( "dqrmt", "TV" ) )
  print( project.get( "dqrmb", "V4" ) )
  print( project.get( "dqrmb" ) )

  sys.exit( 0 )
