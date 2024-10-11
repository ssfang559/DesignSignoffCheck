#!/bin/env python3.7

import os
import re
import sys
import shutil
import hashlib

sys.path.append( "/home/ssfang/bin/" )

import CommonSubString

class Cell():

  def __init__( self, name ):
    self.name = name
    self.instances = dict()

  def addInstance( self, cell, instance ):
    self.instances[ instance ] = cell

  def PrintCell( self ):
    print( "Cell: %s" % ( self.name ) )
    for instance in self.instances.keys():
      print( "  %s" % self.instances[ instance ] )

class Spice():

  def __init__( self, path ):
    temp = ""
    state = ""

    cell = None

    lines = []

    self.top = ""

    self.cells = dict()
    self.idToCell = dict()
    self.cellToId = dict()

    if os.path.exists( path ):

      read = open( path, "r" )

      for line in read.readlines():
        line = re.sub( "\n", "", line )

        if re.match( r'^\s*\+', line ):
          temp = temp + " " + re.sub( "\+", "", line )

        else:
          if temp != "":
            lines.append( temp.split() )
            temp = ""

          temp = line

      circuitStart = ""
      circuitEnd = ""

      circuitMain = []

      for line in lines:
        if line[ 0 ] == ".SUBCKT":
          state = "SUBCKT"
          cell = Cell( line[ 1 ] )

          self.top = line[ 1 ]

          circuitStart = ".SUBCKT"

          for i in range( 2, len( line ) ):
            circuitStart += " " + line[ i ]

          circuitStart += "\n"

        elif line[ 0 ] == ".ENDS":
          state = "ENDS"

          self.cells[ cell.name ] = cell
          circuitEnd = " ".join( line )

          circuit = ""
          circuit += circuitStart
          circuitMain.sort( reverse = True )
          #print("circuitMain")
          #print(circuitMain)
          for temp in circuitMain:
            circuit += temp
          circuit += circuitEnd

          md5 = hashlib.md5( circuit.encode() )

          if md5.hexdigest() not in self.idToCell.keys():
            self.idToCell[ md5.hexdigest() ] = list()

          #self.idToCell[ md5.hexdigest() ] = cell.name
          self.idToCell[ md5.hexdigest() ].append( cell.name )

          self.cellToId[ cell.name ] = md5.hexdigest()

          #print( "=====" )
          #print( circuit )
          #print( "-> " + cell.name + " " + md5.hexdigest() )
          #print( "=====" )

          circuitStart = ""
          circuitEnd = ""
          circuitMain.clear()

        else:
          if state == "SUBCKT":
            circuitTemp = ""

            if re.match( r'^X', line[ 0 ] ):

              cellName = ""

              if "/" in line:
                cellName = line[ line.index( "/" ) + 1 ]

              else:
                cellName = line[ -1 ]

              cell.addInstance( cellName, line[ 0 ] )
              circuitTemp = line[ 0 ]

              end = len( line )

              for i in range( 1, end ):
                if line[ i ] == "/":
                  end = i

              for i in range( 1, end ):
                circuitTemp += " " + line[ i ]

              circuitTemp += "\n"

            elif re.match( r'^M',line[ 0 ] ):
              cell.addInstance( line[ 5 ], line[ 0 ] )
              #circuitTemp = "%s %s %s %s %s %s\n" % ( line[ 0 ], line[ 1 ], line[ 2 ], line[ 3 ], line[ 4 ], line[ 5 ] )
              circuitTemp = " ".join( line ) + "\n"

            elif re.match( r'^D',line[ 0 ] ):
              cell.addInstance( line[ 3 ], line[ 0 ] )
              #circuitTemp = "%s %s %s %s\n" % ( line[ 0 ], line[ 1 ], line[ 2 ], line[ 3 ] )
              circuitTemp = " ".join( line ) + "\n"

            elif re.match( r'^R',line[ 0 ] ):
              cell.addInstance( line[ 3 ], line[ 0 ] )
              #circuitTemp = "%s %s %s %s\n" % ( line[ 0 ], line[ 1 ], line[ 2 ], line[ 3 ] )
              circuitTemp = " ".join( line ) + "\n"

            elif re.match( r'^C',line[ 0 ] ):
              cell.addInstance( line[ 3 ], line[ 0 ] )
              #circuitTemp = "%s %s %s %s\n" % ( line[ 0 ], line[ 1 ], line[ 2 ], line[ 3 ] )
              circuitTemp = " ".join( line ) + "\n"

            if circuitTemp != "":
              circuitMain.append( circuitTemp )

      read.close()

class PercReport():

  def __init__( self, percReportPath, spicePath ):
    count = 0
    placementCount = 0
    maxPlacementCount = 0

    state = ""
    cellName = ""
    deviceName = ""
    deviceType = ""
    deviceSubType = ""
    placementIndex = ""

    placementList = dict()

    self.percReportPath = percReportPath
    self.spicePath = spicePath

    self.placementLists = dict()
    self.violationDevices = dict()

    if os.path.exists( percReportPath ):

      read = open( percReportPath, "r" )

      for line in read.readlines():

        if state == "MN" or state == "MP":
          count += 1
          pins.append( self.GetDeviceInformation( line ) )

          if count == 4:
            count = 0
            state = ""

            device.append( pins )
            self.violationDevices[ cellName ].append( device )

        elif state == "D" or state == "R":
          count += 1
          pins.append( self.GetDeviceInformation( line ) )

          if count == 2:
            count = 0
            state = ""

            device.append( pins )
            self.violationDevices[ cellName ].append( device )

        elif state == "PLACEMENTLISTS":
          matchObjects = re.match( r'^\s*(\S+)?\s+(\S+)\s*\(.+\)', line )

          if matchObjects:
            if count == 0:
              placementIndex = matchObjects.group( 1 )
              maxPlacementCount = int( placementList[ placementIndex ] )
              placementList[ placementIndex ] = dict()
              #print(placementList)

            placementList[ placementIndex ][ matchObjects.group( 2 ) ] = ""

            count += 1

          matchObjects = re.match( r'^\s*(\d+)\s+other\s+placements?\s+\S+\s+skipped\.\.\.$', line )

          if matchObjects:
            count += int( matchObjects.group( 1 ) )

          if count == maxPlacementCount:
            count = 0
            maxPlacementCount = 0

        if re.match( r'^\s*PLACEMENT\s+LISTS\s*\(\s*HCELL\s+STACK\s*\)', line ):
          state = "PLACEMENTLISTS"

        elif re.match( r'^\s*INFORMATION\s+AND\s+WARNINGS$', line ):
          state = "INFORMATIONANDWARNING"

        elif re.match( r'^\s*CELL\s+VERIFICATION\s+RESULTS$', line ):
          state = ""
          placementIndex = ""

          if len( placementList ) > 0:
            self.placementLists[ cellName ] = placementList.copy()

        elif re.match( r'^\s*SUMMARY$', line ):
          if not self.violationDevices[ cellName ] == []:
            pass

          if len( placementList ) > 0:
            self.placementLists[ cellName ] = placementList.copy()

        else:
          matchObjects = re.match( r'^\s*CELL\s+NAME:\s+(\S+)', line )

          if matchObjects:
            state = ""
            cellName = matchObjects.group( 1 )
            placementList.clear()

            self.violationDevices[ cellName ] = []

          matchObjects = re.match( r'^\s*\d+\s+(\S+)\s*\[\s*(\S+)\((\S+)\)\s*\]\s*(\(.*\))?', line )

          if matchObjects:
            pins = list()
            device = list()

            state = matchObjects.group( 2 )

            device.append( matchObjects.group( 1 ) )
            device.append( matchObjects.group( 2 ) )
            device.append( matchObjects.group( 3 ) )

            if not matchObjects.group( 4 ) == None:
              subMatchObjects = re.match( r'^\s*\(\s*(\d+)\s+placements?,\s*LIST#\s*=\s*(\S+)\s*\)', matchObjects.group( 4 ) )

              if subMatchObjects:
                placementList[ subMatchObjects.group( 2 ) ] = subMatchObjects.group( 1 )
                #device.append( subMatchObjects.group( 1 ) )
                device.append( subMatchObjects.group( 2 ) )

            else:
              placementCount += 1
              index = "L" + str( placementCount )
              placementList[ index ] = dict()
              #placementList[ index ][ re.sub( "\/[^\/\s]+$", "", device[ 0 ] ) ] = ""
              #device.append( "1" )
              device.append( index )

        #print( ">" + state + "< >" + str( count ) + "< " + line )

      read.close()

  def GetDeviceInformation( self, line ):
    device = list()

    matchObjects = re.match( r'^\s*(\S+)\s*:\s*(\S+)\s*(\[[^\[\]]+\])?\s*(\[[^\[\]]+\])?\s*(\[[^\[\]]+\])?\s*(\[[^\[\]]+\])?', line )

    if matchObjects:
      device.append( matchObjects.group( 1 ) )
      device.append( matchObjects.group( 2 ) )

      for i in range( 3, 7 ):
        propagations = list()
        device.append( propagations )

        if not matchObjects.group( i ) == None:
          tokens = re.sub( "\[", "", matchObjects.group( i ) )
          tokens = re.sub( "\]", "", tokens )

          for token in tokens.split():
            propagations.append( token )

          propagations.sort()

        else:
          pass

      return device

  def SortByFirst( self, element ):
    return element[ 0 ]

  def SortBySecond( self, element ):
    return element[ 1 ]

  def analyze( self ):

    self.spice = Spice( self.spicePath )

    self.summary = dict()

    secondProcessDevices = list()

    placementLists = dict()
    deviceCellLists = dict()

    for cell in self.spice.cells.keys():
      #self.summary[ cell ] = list()
      self.summary[ cell ] = dict()

    for key in self.violationDevices.keys():
      violationDevices = self.violationDevices[ key ]

      if len( violationDevices ) > 0:
        for violationDevice in violationDevices:
          cell = key

          cells = list()
          cells.append( cell )
            
          instanceNames = violationDevice[ 0 ].split( "/" )
          for instanceName in instanceNames:
            cell = self.spice.cells[ cell ].instances[ instanceName ]
            cells.append( cell )

          device = list()
          device.append( instanceName )
          device.append( cells[ 0 ] )
          device.append( violationDevice )
          #self.summary[ cells[ -2 ] ].append( instanceName )

          #self.summary[ cells[ -2 ] ].append( device )

          if len( instanceNames ) > 1:
            secondProcessDevices.append( device )
            deviceCellLists[ violationDevice[ 0 ] ] = cells

          else:
            #self.summary[ cells[ -2 ] ].append( device )
            md5 = hashlib.md5( str( device ).encode() )
            self.summary[ cells[ -2 ] ][ md5.hexdigest() ] = device
            placementLists[ cells[ -2 ] ] = self.placementLists[ cells[ -2 ] ].copy()

            del cells

    temp = dict()

    for device in secondProcessDevices:
      originalIndex = device[ 2 ][ 3 ]
      originalCell = device[ 1 ]
      originalPlacements = self.placementLists[ originalCell ][ originalIndex ]
      newCell = deviceCellLists[ device[ 2 ][ 0 ] ][ - 2 ]
      deviceName = device[ 2 ][ 0 ]
      placement = re.sub( r'\/[^\/\s]+$', "", deviceName )

      #print( originalCell + " " + newCell + " " + originalIndex )
      #print( originalPlacements )

      device[ 1 ] = newCell
      #device[ 2 ][ 3 ] = newIndex
      device[ 2 ][ 3 ] = ""
      device[ 2 ][ 0 ] = device[ 0 ]
      for pin in device[ 2 ][ 4 ]:
        tokens = pin[ 1 ].split( "/" )
        pin[ 1 ] = tokens[ -1 ]

      md5 = hashlib.md5( str( device ).encode() )

      if md5.hexdigest() not in self.summary[ newCell ].keys():
        self.summary[ newCell ][ md5.hexdigest() ] = device

      if newCell not in placementLists.keys():
        placementLists[ newCell ] = dict()

      #newIndex = "L" + str( len( placementLists[ newCell ] ) + 1 )
      newIndex = "L" + str( len( self.summary[ newCell ] ) )

      #print( newIndex )
      device[ 2 ][ 3 ] = newIndex

      #print( device )
      #print( md5.hexdigest() )

      if newIndex not in placementLists[ newCell ].keys():
        placementLists[ newCell ][ newIndex ] = dict()

      if len( originalPlacements.keys() ) == 0:
        placementLists[ newCell ][ newIndex ][ placement ] = ""
          
      else:
        for placementPrefix in originalPlacements.keys():
          placementLists[ newCell ][ newIndex ][ placementPrefix + "/" + placement ] = ""

    for cellList in deviceCellLists:
      del cellList
    del deviceCellLists

    for cell in list( self.placementLists.keys() ):
      for index in list( self.placementLists[ cell ].keys() ):
        for placement in self.placementLists[ cell ][ index ]:
          del placement
        del self.placementLists[ cell ][ index ]
      del self.placementLists[ cell ]
    del self.placementLists
    
    self.placementLists = placementLists

    #print( "CELL VIOLATION" )
    #for cell in self.violationDevices.keys():
    #  self.violationDevices[ cell ].sort( key = SortByFirst )
    #  print( "" + cell )
    #  for device in self.violationDevices[ cell ]:
    #    if len( device ) == 6:
    #      print( "  %s %s %s %s %s" % ( device[ 0 ], device[ 1 ], device[ 2 ], device[ 3 ], device[ 4 ] ) )
    #      for pin in device[ 5 ]:
    #        print( "    %s %s %s %s %s %s" % ( pin[ 0 ], pin[ 1 ], pin[ 2 ], pin[ 3 ], pin[ 4 ], pin[ 5 ] ) )

    #    else:
    #      print( "  %s %s %s" % ( device[ 0 ], device[ 1 ], device[ 2 ] ) )

    #      for pin in device[ 3 ]:
    #        print( "    %s %s %s %s %s %s" % ( pin[ 0 ], pin[ 1 ], pin[ 2 ], pin[ 3 ], pin[ 4 ], pin[ 5 ] ) )

    print( "VIOLATION DEVICE PLACEMENT" )
    for cell in placementLists.keys():
      print( "  %s" % ( cell ) )

      placements = placementLists[ cell ]

      for key in placements.keys():
        print( "    %s" % ( key ) )

        for placement in placements[ key ].keys():
          print( "      %s" % ( placement ) )

      print( "" )

    sortedCells = []

    for cell in self.summary.keys():
      length = len( self.summary[ cell ] )

      if length > 0:
        sortedCells.append( [ cell, length ] )

    sortedCells.sort( key = self.SortByFirst )
    sortedCells.sort( key = self.SortBySecond, reverse = True )

    print( "VIOLATIONS" )

    for cell in sortedCells:
      print( "  %d %s" % ( cell[ 1 ], cell[ 0 ] ) )

    print( "" )

def SortByFirst( element ):
  return element[ 0 ]

def SortBySecond( element ):
  return element[ 1 ]

def DevicesComparison( oldDevice, newDevice ):
  if ( newDevice > oldDevice ) - ( newDevice < oldDevice ) == 0:
    return True

  else:
    return False

def NewPlacementIsInOldPlacement( oldPlacements, newPlacements ):
  for newPlacement in newPlacements.keys():
    for key in oldPlacements:
      for oldPlacement in oldPlacements[ key ].keys():
        if newPlacement == oldPlacement:
          return True

  return False

def FindSimiliarCell( targetCell, cells, ratio ):

  commonSubString = CommonSubString.CommonSubString()

  maxSimiliarRatio = 0

  similiarCell = ""
  subString = ""

  similiarCells = list()

  for cell in cells:

    commonSubString.compare1( targetCell, cell )
    string = commonSubString.getStrings()

    if len( cell ) > len( targetCell ):
      similiarRatio = len( string ) / len( targetCell )
    else:
      similiarRatio = len( string ) / len( cell )

    if similiarRatio > maxSimiliarRatio:
      maxSimiliarRatio = similiarRatio
      similiarCell = cell
      subString = string

    if similiarRatio > ratio:
      similiarCells.append( cell )

    if ( os.getenv( "DEBUG", default = None ) ):
      print( "%s -> %f" % ( cell, similiarRatio ) )

  #print( "%s %s %s %f" % ( targetCell, similiarCell, subString, maxSimiliarRatio ) )

  #return [ similiarCell, maxSimiliarRatio ]
  return similiarCells

def CompareDevice( deviceA, deviceB ):

  if deviceA[ 2 ][ 0 ] != deviceB[ 2 ][ 0 ]:
    #print( "Name is inconsistant" )

    return False

  elif deviceA[ 2 ][ 1 ] != deviceB[ 2 ][ 1 ]:
    #print( "Type is inconsistant" )

    return False

  elif deviceA[ 2 ][ 2 ] != deviceB[ 2 ][ 2 ]:
    #print( "Subtype is inconsistant" )

    return False

  #elif deviceA[ 2 ][ 3 ] != deviceB[ 2 ][ 3 ]:
    #print( "Label is inconsistant" )

  #  return False

  else:

    if len( deviceA[ 2 ][ 4 ] ) != len( deviceB[ 2 ][ 4 ] ):
      #print( "Pin count is inconsistant" )

      return False

    else:

      for i in range( 0, len( deviceA[ 2 ][ 4 ] ) ):

        if deviceA[ 2 ][ 4 ][ i ][ 0 ] != deviceB[ 2 ][ 4 ][ i ][ 0 ]:
          #print( "Pin is inconsistant" )

          return False

        #elif deviceA[ 2 ][ 4 ][ i ][ 1 ] != deviceB[ 2 ][ 4 ][ i ][ 1 ]:
          #print( "Net is inconsistant" )

        #  return False

        else:
          for j in range( 2, len( deviceA[ 2 ][ 4 ][ i ] ) ):
            if not set( deviceB[ 2 ][ 4 ][ i ][ j ] ).issubset( deviceA[ 2 ][ 4 ][ i ][ j ] ):
              #print( "Path is not subset" )

              return False

  return True

def Compare( percReportOld, percReportNew, waivedListOld ):
  print( "PREVIOUS VIOLATIONS" )

  for cell in percReportOld.summary.keys():
    if len( percReportOld.summary[ cell ] ) > 0:
      print( "  CELL %s" % ( cell ) )

      for device in percReportOld.summary[ cell ].values():
        print( "    %s %s %s %s" % ( device[ 2 ][ 0 ], device[ 2 ][ 1 ], device[ 2 ][ 2 ], device[ 2 ][ 3 ] ) )

        for pin in device[ 2 ][ 4 ]:
          print( "      %s %s" % ( pin[ 0 ], pin[ 1 ] ), end = '' )

          for i in range( 2, len( pin ) ):
            print( " [", end = '' )
            for propagate in pin[ i ]:
              print( " %s" % ( propagate ), end = '' )

            print( " ]", end = '' )

          print( "" )

  print( "" )
  print( "CURRENT VIOLATIONS" )

  for cell in percReportNew.summary.keys():
    if len( percReportNew.summary[ cell ] ) > 0:
      print( "  CELL %s" % ( cell ) )

      for device in percReportNew.summary[ cell ].values():
        print( "    %s %s %s %s" % ( device[ 2 ][ 0 ], device[ 2 ][ 1 ], device[ 2 ][ 2 ], device[ 2 ][ 3 ] ) )

        for pin in device[ 2 ][ 4 ]:
          print( "      %s %s" % ( pin[ 0 ], pin[ 1 ] ), end = '' )

          for i in range( 2, len( pin ) ):
            print( " [", end = '' )
            for propagate in pin[ i ]:
              print( " %s" % ( propagate ), end = '' )

            print( " ]", end = '' )

          print( "" )

  print( "" )

  previousWaivedCells = []

  waivedCells = dict()
  violationCells = dict()

  if os.path.exists( waivedListOld ):
    read = open( waivedListOld, "r" )

    for line in read.readlines():
      line = re.sub( "\n", "", line )
      previousWaivedCells.append( line )

    read.close()

  #for cell in percReportNew.summary.keys():
  #  if len( percReportNew.summary[ cell ] ) > 0:
  #    newCellId = percReportNew.spice.cellToId[ cell ]

  #    if newCellId in percReportOld.spice.idToCell.keys():
  #      oldCellName = percReportOld.spice.idToCell[ newCellId ]

  #      print( "OLD CELL: " + oldCellName )

  #      if oldCellName in previousWaivedCells:
  #        waivedCells[ cell ] = []

  #        for device in percReportNew.summary[ cell ]:
  #          print( "CELL: %s, DEVICE: %s waived" % ( cell, device ) )
  #          waivedCells[ cell ].append( device )

  #      else:
  #        violationCells[ cell ] = []

  #        for device in percReportNew.summary[ cell ]:
  #          print( "CELL: %s, DEVICE: %s is new violation" % ( cell, device ) )
  #          violationCells[ cell ].append( device )

  #    else:
  #      violationCells[ cell ] = []

  #      for device in percReportNew.summary[ cell ]:
  #        print( "CELL: %s, DEVICE: %s is new violation" % ( cell, device ) )
  #        violationCells[ cell ].append( device )

  for cell in percReportNew.summary.keys():

    waivedCells[ cell ] = []
    violationCells[ cell ] = []

    if len( percReportNew.summary[ cell ] ) > 0:

      if( os.getenv( "DEBUG", default = None ) ):
        print( "Check CELL: %s" % ( cell ) )

      newCellId = percReportNew.spice.cellToId[ cell ]

      oldCellName = ""

      oldCellNames = list()

      if newCellId in percReportOld.spice.idToCell.keys():

        #oldCellName = percReportOld.spice.idToCell[ newCellId ]
        oldCellNames = percReportOld.spice.idToCell[ newCellId ]

      elif ( ( cell in percReportOld.spice.cells.keys() ) \
             and \
             ( cell in percReportNew.spice.cells.keys() ) \
           ):

        oldCellNames.append( cell )

      else:
        comparisonResult = FindSimiliarCell( cell, percReportOld.spice.cells.keys(), 0.9 )

        #if comparisonResult[ 1 ] > 0.9:
        #  oldCellName = comparisonResult[ 0 ]
        if comparisonResult is not None:
          oldCellNames = comparisonResult

      #print( "Current Cell: %s" % ( cell ) )
      #print( "  " + newCellId )
      #print( "Prevoius Cell: %s" % ( str( oldCellNames ) ) )

      print( "%32s %32s %16s %8s %s" % ( "PREVIOUS", "CURRENT", "DEVICE", "STATUS", "REMARK" ), end = '\n\n' )

      if len( oldCellNames ) > 0:

        mostPassedDeviceCellName = ""

        mostPassedDevices = list()
        mostPassedDeviceCellFailDevices = list()

        for oldCellName in oldCellNames:

          #print( "  " + oldCellName + " (" + percReportOld.spice.cellToId[ oldCellName ] + ")" )

          if oldCellName in previousWaivedCells:

            #print( "  " + oldCellName + " is in the waived list" )
            #oldPlacementLists = percReportOld.placementLists[ oldCellName ]

            passedDevices = list()
            failedDevices = list()

            for deviceID, device in percReportNew.summary[ cell ].items():

              deviceFailed = True

              if deviceID in percReportOld.summary[ oldCellName ].keys():
                deviceFailed = False

              else:
                for oldDevice in percReportOld.summary[ oldCellName ].values():
                  if CompareDevice( oldDevice, device ):
                    deviceFailed = False

              if deviceFailed:
                failedDevices.append( device )

              else:
                passedDevices.append( device )

            #print( "  failedDevices = " + str(failedDevices ) )
            #print( "  passedDevices = " + str( passedDevices ) )

            #for device in percReportNew.summary[ cell ].values():

            #  newDeviceOriginalCell = device[ 1 ]
            #  newDevicePlacementListIndex = device[ 2 ][ 3 ]
            #  newPlacementLists = percReportNew.placementLists[ newDeviceOriginalCell ][ newDevicePlacementListIndex ]

            #  if NewPlacementIsInOldPlacement( oldPlacementLists, newPlacementLists ):
            #    passedDevices.append( device )

            #  else:
            #    failedDevices.append( device )

            if len( passedDevices ) >= len( mostPassedDevices ):
              mostPassedDeviceCellName = oldCellName
              mostPassedDevices = passedDevices
              mostPassedDeviceCellFailDevices = failedDevices

        #print( "  mostPassedDeviceCellName = " + mostPassedDeviceCellName )

        if mostPassedDeviceCellName != "":

          for device in mostPassedDevices:
            print( "%32s %32s %16s %8s %s" % ( mostPassedDeviceCellName, cell, device[ 0 ], "PASS", "In the previous waived list" ) )
            waivedCells[ cell ].append( device )

          for device in mostPassedDeviceCellFailDevices:
            print( "%32s %32s %16s %8s %s" % ( mostPassedDeviceCellName, cell, device[ 0 ], "FAIL", "In the waived list but instance name, type, subtype, label, or pins' connection is inconsistant" ) )
            violationCells[ cell ].append( device )

        else:
          if len( oldCellNames ) == 0:
            for device in percReportNew.summary[ cell ].values():
              print( "%32s %32s %16s %8s %s" % ( "None", cell, device[ 0 ], "FAIL", "May be a new cell. Cannot match all the following previous cells:" ) )
              for oldCell in oldCellNames:
                print( "%32s %32s %16s %8s %s" % ( "", "", "", "", "  " + oldCell ) )

              #violationCells[ cell ].append( device[ 0 ] )

          else:
            for device in percReportNew.summary[ cell ].values():
              #print( "%32s %32s %16s %8s %s" % ( "None", cell, device[ 0 ], "FAIL", "It's a new violation. All of the following previous cells are PASS:" ) )
              print( "%32s %32s %16s %8s %s" % ( "None", cell, device[ 0 ], "FAIL", "It's a new violation. All of the following cells in previous version are PASS:" ) )
              for oldCell in oldCellNames:
                print( "%32s %32s %16s %8s %s" % ( "", "", "", "", "  " + oldCell ) )

          violationCells[ cell ].append( device )

      else:
        for device in percReportNew.summary[ cell ].values():
          print( "%32s %32s %16s %8s %s" % ( "None", cell, device[ 0 ], "FAIL", "It's a new cell and violation." ) )
          violationCells[ cell ].append( device )

      print( "" )

  write = open( "waived_cells", "w" )

  for cell in waivedCells.keys():
    if len( waivedCells[ cell ] ) > 0:
      write.write( cell + "\n" )

  write.close()

  sortedCells = []

  for cell in violationCells.keys():
    length = len( violationCells[ cell ] )

    if length > 0:
      sortedCells.append( [ cell, length ] )

  sortedCells.sort( key = SortByFirst )
  sortedCells.sort( key = SortBySecond, reverse = True )

  writeReport = open( "summary.rpt", "w" )

  writeReport.write( "VIOLATIONS:\n" )
  writeReport.write( "\n" )

  count = 0

  if len( sortedCells ):
    for cell in sortedCells:
      writeReport.write( "%d %s\n" % ( cell[ 1 ], cell[ 0 ] ) )
      count += cell[ 1 ]

  else:
    writeReport.write( "  NONE\n" )

  writeReport.write( "\n" )
  writeReport.write( "TOTAL VIOLATIONS: %d\n" % ( count ) )
  writeReport.write( "\n" )

  writeReport.write( "WAIVED VIOLATIONS:\n" )
  writeReport.write( "\n" )

  sortedCells = []

  for cell in waivedCells.keys():
    length = len( waivedCells[ cell ] )

    if length > 0:
      sortedCells.append( [ cell, length ] )

  sortedCells.sort( key = SortByFirst )
  sortedCells.sort( key = SortBySecond, reverse = True )

  count = 0

  if len( sortedCells ):
    for cell in sortedCells:
      writeReport.write( "%d %s\n" % ( cell[ 1 ], cell[ 0 ] ) )
      count += cell[ 1 ]

  else:
    writeReport.write( "  NONE\n" )

  writeReport.write( "\n" )
  writeReport.write( "TOTAL WAIVED VIOLATIONS: %d" % ( count ) )
  writeReport.write( "\n" )

  writeReport.close()

  write = open( "wesign_summary.rpt", "w" )
  
  check = os.path.basename( os.getcwd() )

  #write.write( check )
  #write.write( "\n" )

  for cell in violationCells.keys():
    if len( violationCells[ cell ] ) > 0:
      for device in violationCells[ cell ]:
        placement = next( iter( percReportNew.placementLists[ cell ][ device[ 2 ][ 3 ] ] ) )
        instance = placement + "/" + device[ 2 ][ 0 ]
        matchAF1 = re.match( r'.*ANALOG.*', instance, re.I )
        matchAF2 = re.match( r'.*AF.*', instance )
        matchIO = re.match( r'.*_IO_.*', instance )
        matchRAS1 = re.match( r'.*ARY.*', instance )
        matchRAS2 = re.match( r'.*ARRAY.*', instance, re.I )
        matchDC = re.match(r'.*_DC_.*', instance)
        if matchAF1 or matchAF2 or cell.startswith( "F_" ) or cell.startswith( "AF_" ) :
            part = "AF"
        elif cell.startswith( "ESD_" ) or cell.startswith( "IO_" ) or matchIO:
            part = "IO"
        elif matchRAS1 or matchRAS2 or cell.startswith( "R_" ):
            part = "RAS"
        elif cell.startswith( "D_" ) or matchDC:
            part = "DC"
        elif cell.startswith( "C_" ):
            part = "DATA"
        else:
            part = "DC"
        write.write( check + ", " + instance + ", " + cell + ", " + part )
        write.write( "\n" )

  #for cell in waivedCells.keys():
  #  if len( waivedCells[ cell ] ) > 0:
  #    for device in waivedCells[ cell ]:
  #      placement = next( iter( percReportNew.placementLists[ cell ][ device[ 2 ][ 3 ] ] ) )
  #      instance = placement + "/" + device[ 2 ][ 0 ]
  #      write.write( "WAIVED, " + cell + ", " + instance )
  #      write.write( "\n" )

  write.close()

if __name__ == "__main__":
  percReportOld = PercReport( sys.argv[ 1 ], sys.argv[ 2 ] )
  percReportNew = PercReport( sys.argv[ 3 ], sys.argv[ 4 ] )

  percReportOld.analyze()
  percReportNew.analyze()

  waivedListOld = sys.argv[ 5 ]

  Compare( percReportOld, percReportNew, waivedListOld )
