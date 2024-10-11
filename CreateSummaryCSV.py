#!/bin/env python3.7

import os
import re
import csv
import sys
import glob

class DesignSignoffCheck():

  def __init__( self, path ):

    self.date = ""
    self.version = ""

    self.checks = list()

    self.summaries = dict()

    if os.path.exists( path ):

      self.date = self.GetDate( path )
      self.version = self.GetVersion( path )

      directories = glob.glob( path + "/*" )

      for directory in directories:
        check = os.path.basename( directory )

        if check != "database":
          summary = [ directory ] + self.AnalysisSummaryReport( directory + "/summary.rpt" )
          self.checks.append( check )
          self.summaries[ check ] = summary

  def getVersion( self ):
    return self.version

  def getDate( self ):
    return self.date

  def getChecks( self ):
    return self.checks

  def getCheckWorkingDirectory( self, check ):
    if check in self.summaries.keys():
      return self.summaries[ check ][ 0 ]

    else:
      return None

  def getResult( self, check ):
    if check in self.summaries.keys():
      result = ""

      summary = self.summaries[ check ]

      if len( summary[ 2 ] ) == 0:
        result = "PASSED"

      else:
        result = "FAILED"

      return [ result, summary[ 2 ], summary[ 4 ] ]

    else:
      return None

  def getCheckTotalWaiving( self, check ):
    return self.summaries[ check ][ 3 ]

  def getCheckTotalViolation( self, check ):
    return self.summaries[ check ][ 1 ]

  def writeCSV( self ):

    head = list()
    head.append( "Edit Number" )
    head.append( "Count (Hier)" )
    head.append( "" )
    head.append( "Part" )
    head.append( "Revised Part" )
    head.append( "Comment" )

    empty = list()

    for i in range( 0, 6 ):
      empty.append( "" )

    for check in self.summaries.keys():

      summary = self.summaries[ check ]

      fileName = re.sub( r'_', "", check ) + ".csv"
      violations = summary[ 2 ]
      waives = summary[ 4 ]

      write = open( fileName, "w" )

      csvWrite = csv.writer( write )

      head[ 2 ] = "Violated Cell"

      csvWrite.writerow( head )

      for line in violations:
        csvWrite.writerow( line )

      csvWrite.writerow( empty )

      head[ 2 ] = "Waived Cell"

      csvWrite.writerow( "" )
      csvWrite.writerow( head )

      for line in waives:
        csvWrite.writerow( line )

      csvWrite.writerow( empty )

      write.close()

  def GetVersion( self, path ):
    return path.split( "/" )[ -2 ]

  def GetDate( self, path ):

    date = ""
    timeStampFilePath = path + "/database/TIMESTAMP"

    if os.path.exists( timeStampFilePath ):
      read = open( timeStampFilePath )

      for line in read.readlines():
        date = re.sub( r'\n$', "", line )

      read.close()

    return date

  def AnalysisSummaryReport( self, path ):
    waiveCount = 1
    violationCount = 1

    totalWaives = 0
    totalViolations = 0

    state = ""

    waives = list()
    violations = list()

    if os.path.exists( path ):

      read = open( path )

      for line in read.readlines():
        if re.match( r'^VIOLATIONS:', line ):
          state = "VIOLATION"

        elif re.match( r'^WAIVED VIOLATIONS:', line ):
          state = "WAIVED"

        else:
          matchObject = re.match( r'^(\d+)\s+(\S+)$', line )

          if matchObject:
            if state == "VIOLATION":
              violation = list()

              violation.append( violationCount )
              violation.append( matchObject.group( 1 ) )
              violation.append( matchObject.group( 2 ) )
              violation.append( "" )
              violation.append( "" )
              violation.append( "" )

              violations.append( violation )

              violationCount += 1
              totalViolations += int( matchObject.group( 1 ) )

            elif state == "WAIVED":
              waive = list()

              waive.append( waiveCount )
              waive.append( matchObject.group( 1 ) )
              waive.append( matchObject.group( 2 ) )
              waive.append( "" )
              waive.append( "" )
              waive.append( "" )

              waives.append( waive )

              waiveCount += 1
              totalWaives += int( matchObject.group( 1 ) )

      read.close()

    return [ totalViolations, violations, totalWaives, waives ]

if __name__ == "__main__":

  previousCheck = DesignSignoffCheck( sys.argv[ 1 ] )

  latestCheck = DesignSignoffCheck( sys.argv[ 2 ] )
  latestCheck.writeCSV()

  write = open( sys.argv[ 3 ], "w" )

  csvWrite = csv.writer( write )

  line = list()

  line.append( "Edit Number" )
  line.append( "Design Sign-Off PERC Check" )
  line.append( previousCheck.getVersion() + " Results" )
  line.append( latestCheck.getVersion() + " Results" )
  line.append( "Remark" )
  line.append( "Path & Detail (perc.rep & svdb)" )

  csvWrite.writerow( line )

  line.clear()

  line.append( "" )
  line.append( "" )
  line.append( previousCheck.getDate() )
  line.append( latestCheck.getDate() )
  line.append( previousCheck.getVersion() + " to " + latestCheck.getVersion() )
  line.append( "" )
  line.append( "" )

  csvWrite.writerow( line )

  count = 1

  allChecks = list( set( previousCheck.getChecks() + latestCheck.getChecks() ) )
  allChecks.sort()

  for check in allChecks:

    line.clear()

    line.append( count )
    line.append( check )

    previousCheckResult = previousCheck.getResult( check )
    latestCheckResult = latestCheck.getResult( check )
    latestCheckResultViolations = 0
    latestCheckResultWaives = 0

    if previousCheckResult is not None:
      line.append( previousCheckResult[ 0 ] )

    else:
      line.append( "NONE" )

    if latestCheckResult is not None:
      line.append( latestCheckResult[ 0 ] )
      latestCheckResultViolations = latestCheck.getCheckTotalViolation( check )
      latestCheckResultWaives = latestCheck.getCheckTotalWaiving( check )

    else:
      line.append( "NONE" )

    if latestCheckResultViolations > 0 or latestCheckResultWaives > 0:
      line.append( "Violation: %d" % ( latestCheckResultViolations ) )

    else:
      line.append( "" )

    line.append( "perc.rep" )

    if latestCheckResult is not None:
      line.append( "%s/perc.rep" % ( latestCheck.getCheckWorkingDirectory( check ) ) )

    else:
      line.append( "NONE" )

    csvWrite.writerow( line )

    line.clear()

    line.append( "" )
    line.append( "" )
    line.append( "" )
    line.append( "" )

    if latestCheckResultViolations > 0 or latestCheckResultWaives > 0:
      line.append( "Waive: %d" % ( latestCheckResultWaives ) )

    else:
      line.append( "" )

    line.append( "svdb" )

    if latestCheckResult is not None:
      line.append( "%s/svdb" % ( latestCheck.getCheckWorkingDirectory( check ) ) )

    else:
      line.append( "NONE" )

    csvWrite.writerow( line )

    count += 1

  sys.exit( 0 )
