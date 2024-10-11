#!/bin/env python3.7

import os
import re
import sys
import glob
import stat
import time
import shutil
import signal
import threading
import subprocess

sys.path.append( "/home/leopeng/bin" )

import Calibre
import ProjectInfo
import ArgumentsProcessor

gWorkingDirectory = ""

gCDLStreamOutScriptPath = "/apps/imctf/cad/script/Ferrari/IMCP/vir/strmCDL/strmCDL.py"
gCDLModificationScriptPath = "/home/cad1/kobe/PERC/cxmt10G4/Latest/Other/patch_res_values.pl"
gDesignSignoffCheckMainPath = "/home/cad1/kobe/PERC/cxmt10G4/Latest/Main/*/"
gPercReportComparisonScriptPath = "/home/cad1/kobe/PERC/cxmt10G4/Latest/Other/compare_perc_report.py"
gDesignSignoffCheckCSVtoExcelPath = "/home/cad1/kobe/PERC/cxmt10G4/Latest/Other/DesignSignoffCheckCSVtoExcel.py"
gDesignSignoffCheckCSVCreationPath = "/home/cad1/kobe/PERC/cxmt10G4/Latest/Other/CreateSummaryCSV.py"
gDesignSignoffCheckResultForWesignCSV = "/home/cad1/kobe/PERC/cxmt10G4/Latest/Other/WesignSummaryCSV.py"

def RunCalibre( argv ):
  os.system( argv )

#Signal handler, frame-stack
def Interrupt( siignal_received, frame ):

  jobs = glob.glob( gWorkingDirectory + "/*/job.id" )

  write = open( gWorkingDirectory + "/interrupt.log", "w" )

  for job in jobs:
    read = open( job, "r" )

    for line in read.readlines():
      matchObject = re.match( r'^\s*Job\s+<(\S+)>\s+is\s+submitted\s+to\s+queue\s+<(\S+)>.$', line )

      if matchObject:
        identify = matchObject.group( 1 )
        queue = matchObject.group( 2 )
        command = "bkill " + matchObject.group( 1 )
        subprocess.call( command, shell = True, stdout = write, stderr = write )
        print( "[WARNING] KILL JOB " + identify + " FROM QUEUE " + queue + "..." )

    read.close()

  write.close()

  sys.exit( 0 )

if __name__ == "__main__":

  root = os.getcwd()

  checks = list()

  setting = dict()
  arguments = dict()

  arguments[ "model" ] = list()
  arguments[ "runDir" ] = list()
  arguments[ "viewName" ] = list()
  arguments[ "model" ].append( "LVS" )
  arguments[ "runDir" ].append( "./" )
  arguments[ "viewName" ].append( "schematic" )

  #Get dict of ArgumentsProcessor
  temp = ArgumentsProcessor.ArgumentsProcessor()
  temp = temp.get()

  #Add ArgumentsProcessor (keys,values) to arguments eg:{calibre:2020.1_36.18,project:drjoa,libname:10G4_16GDDR5_MDIE_BT00_DLT00,cellName:MDIE_FULLCHIP,perVersion:,version:V0}
  for key in temp.keys():
    arguments[ key ] = temp[ key ]

  #Get projects information  
  temp = ProjectInfo.ProjectInfo()
  temp = temp.get( arguments[ "project" ][ 0 ],version=arguments["version"][0])

  #Add projects information keys(process,metalScheme,cdsLib,incFile,simrc) to arguments,and add values to arguments
  for key in temp:
    arguments[ key ] = list()

    if type( temp[ key ] ) is str:
      arguments[ key ].append( temp[ key ] )

    elif type( temp[ key ] ) is list:
      for value in temp[ key ]:
        arguments[ key ].append( value )

  #Interrupt from keyboard. (ctrl+c)
  signal.signal( signal.SIGINT, Interrupt )

#Creating directory V0 as working directory.
  gWorkingDirectory = root + "/" + arguments[ "version" ][ 0 ]

  if os.path.exists( gWorkingDirectory ) and "rerun" in arguments.keys():

    if len( arguments[ "rerun" ] ) == 0:
      print( "[INFO] REMOVING DIRECTORY \"%s\"" % ( arguments[ "version" ][ 0 ] ) )
      shutil.rmtree( arguments[ "version" ][ 0 ] )

    else:
      for check in arguments[ "rerun" ]:
        os.remove( gWorkingDirectory + "/" + check + "/DONE" )

  if not os.path.exists( gWorkingDirectory ):
    print( "[INFO] CREATING DIRECTORY AT \"%s\"" % ( gWorkingDirectory ) )
    os.mkdir( gWorkingDirectory )

  os.chdir( gWorkingDirectory )

#Copy gDesignSignoffCheckMainPath to V0,and link *.perc to PERC rule.
  for fromPath in glob.glob( gDesignSignoffCheckMainPath ):

    check = fromPath.split( "/" )[ -2 ]

    toPath = gWorkingDirectory + "/" + check

    if not os.path.exists( toPath ):
      shutil.copytree( fromPath, toPath )

    deck = glob.glob( "./" + check + "/*.perc" )

    if len( deck ) > 0:
      symbolicLink = "./" + check + "/calibrePERC.rule"

      if not os.path.exists( symbolicLink ):
        os.symlink( os.path.basename( deck[ 0 ] ), symbolicLink )

      checks.append( check )

  checks.sort()

#Write files to subdirectories of V0. (run.csh and run_compare_perc_report.csh)
  for check in checks:

    previousPERCReport = ""
    previousSpiceNetlist = ""
    previousWaivedList = ""

    #Create calibre instance
    calibre = Calibre.Calibre()

    percReportComparison = gPercReportComparisonScriptPath
    calibreHomePath = calibre.getHome( arguments[ "calibre" ][ 0 ] )
    runCalibre = "./" + check + "/run.csh"
    runComparison = "./" + check + "/run_compare_perc_report.csh"
    currentPERCReport = gWorkingDirectory + "/" + check + "/perc.rep"
    currentSpiceNetlist = gWorkingDirectory + "/database/" + arguments[ "libName" ][ 0 ] + "_" + arguments[ "cellName" ][ 0 ] + ".cdl"

    if os.path.exists( root + "/" + arguments[ "preVersion" ][ 0 ] + "/" ):
      previousPERCReport = root + "/" + arguments[ "preVersion" ][ 0 ] + "/" + check + "/perc.rep"
      previousSpiceNetlist = glob.glob( root + "/" + arguments[ "preVersion" ][ 0 ] + "/database/*.cdl" )
      previousWaivedList = root + "/" + arguments[ "preVersion" ][ 0 ] + "/" + check + "/waived_cells"

    voltageInformation = gWorkingDirectory + "/database/voltfile_" + arguments[ "project" ][ 0 ] + "_" + arguments[ "cellName" ][ 0 ]

    if len( previousSpiceNetlist ) > 1:
      count = 0
      print( "[INFO] FOUND MULTIPLE SPICE NETLISTS AT %s. CHOOSE THE FIRST ONE AS COMPARISON TARGET." % ( root + "/" + arguments[ "preVersion" ][ 0 ] + "/database" ) )

      for spice in previousSpiceNetlist:
        count += 1
        print( "         [" + count + "] " + spice )

      print( "\n" )

      previousSpiceNetlist = previousSpiceNetlist[ 0 ]

    elif len( previousSpiceNetlist ) == 1:
      previousSpiceNetlist = previousSpiceNetlist[ 0 ]

    elif len( previousSpiceNetlist ) == 0:
      previousSpiceNetlist = ""

    write = open( runCalibre, "w" )

    write.write( "#!/bin/csh -f\n" )
    write.write( "\n" )
    write.write( "setenv CALIBRE_HOME \"" + calibreHomePath + "\"\n" )
    write.write( "setenv PERC_SCHCELLNAME \"" + arguments[ "cellName" ][ 0 ] + "\"\n" )
    write.write( "setenv PERC_LAYCELLNAME \"" + arguments[ "cellName" ][ 0 ] + "\"\n" )
    write.write( "setenv PERC_PROCESS \"" + arguments[ "process" ][ 0 ] + "\"\n" )
    write.write( "setenv PERC_METSCHEME \"" + arguments[ "metalScheme" ][ 0 ] + "\"\n" )
    write.write( "setenv PERC_SCHNETLIST \"" + currentSpiceNetlist + "\"\n" )
    write.write( "setenv PERC_LAYNETLIST \"\"\n" )
    write.write( "setenv PERC_GDSFILE \"\"\n" )
    write.write( "setenv PERC_HCELL \"\"\n" )
    write.write( "setenv PERC_VOLTAGEFILE \"" + voltageInformation + "\"\n" )
    write.write( "setenv VOLTAGE_FILE \"" + voltageInformation + "\"\n" )
    write.write( "setenv PERC_INPUTFILES \"\"\n" )
    write.write( "setenv PERC_ISCHIPTOP \"NO\"\n" )
    write.write( "setenv PERC_VERSION \"0.3.0\"\n" )
    write.write( "\n" )
    write.write( "calibre -perc -hier -turbo calibrePERC.rule >& run.log\n" )
    write.write( "run_compare_perc_report.csh\n" )
    write.write( "touch DONE\n" )
    write.write( "exit\n" )

    write.close()

    os.chmod( runCalibre, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

    write = open( runComparison, "w" )

    write.write( "#!/bin/csh -f\n" )
    write.write( "\n" )
    write.write( "set perc_compare = \"" + percReportComparison + "\"\n" )
    write.write( "$perc_compare \"" + previousPERCReport + "\" \\\n" )
    write.write( "              \"" + previousSpiceNetlist + "\" \\\n" )
    write.write( "              \"" + currentPERCReport + "\" \\\n" )
    write.write( "              \"" + currentSpiceNetlist + "\" \\\n" )
    write.write( "              \"" + previousWaivedList + "\" >& compare_perc_report.log\n" )
    write.write( "exit\n" )

    write.close()

    os.chmod( runComparison, stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

# database/    purpose:to stream out a netlist.
# Write files to database directory and run them. (cdl_stream_out.js, run_cdl_stream_out.csh, run_netlist_postprocessing.csh, DONE)
  os.chdir( gWorkingDirectory + "/database" )

  write = open( "cdl_stream_out.js", "w" )

  write.write( "{\n" )
  write.write( "  \"cdsLib\" : \"%s\",\n" % arguments[ "cdsLib" ][ 0 ] )
  write.write( "  \"libName\" : \"%s\",\n" % arguments[ "libName" ][ 0 ] )
  write.write( "  \"cellName\" : \"%s\",\n" % arguments[ "cellName" ][ 0 ] )
  write.write( "  \"viewName\" : \"%s\",\n" % arguments[ "viewName" ][ 0 ] )
  write.write( "  \"model\" : \"%s\",\n" % arguments[ "model" ][ 0 ] )
  write.write( "  \"runDir\" : \"%s\",\n" % arguments[ "runDir" ][ 0 ] )
  write.write( "  \"incFile\" : \"%s\",\n" % arguments[ "incFile" ][ 0 ] )
  write.write( "  \"simrc\" : \"%s\"\n" % arguments[ "simrc" ][ 0 ] )
  write.write( "}" )

  write.close()

  write = open( "run_cdl_stream_out.csh", "w" )

  write.write( "#!/bin/csh -f\n" )
  write.write( "\n" )
  write.write( gCDLStreamOutScriptPath + " cdl_stream_out.js >& cdl_stream_out.log\n" )
  write.write( "exit\n" )

  write.close()

  os.chmod( "run_cdl_stream_out.csh", stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

  spiceNetlist = gWorkingDirectory + "/database/" + arguments[ "libName" ][ 0 ] + "_" + arguments[ "cellName" ][ 0 ] + ".cdl"

  write = open( "run_netlist_postprocessing.csh", "w" )

  write.write( "#!/bin/csh -f\n" )
  write.write( "\n" )
  write.write( "set root = `pwd`\n" )
  write.write( "set input = \"./temp_strmCDL/%s.cdl\"\n" % ( arguments[ "cellName" ][ 0 ] ) )
  write.write( "set output = \"%s\"\n" % ( spiceNetlist ) )
  write.write( gCDLModificationScriptPath + " -p " + arguments[ "process" ][ 0 ] + " -i $input -o $output\n" )
  write.write( "exit\n" )

  write.close()

  os.chmod( "run_netlist_postprocessing.csh", stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

  if not os.path.exists( spiceNetlist ):

    print( "[INFO] STREAM OUT SPICE NETLIST..." )

    command = "date +%Y/%m/%d > TIMESTAMP"

    subprocess.call( command, shell = True, stdout = None, stderr = None )

    write = open( "run.csh", "w" )

    write.write( "#!/bin/csh -f\n" )
    write.write( "\n" )
    write.write( "run_cdl_stream_out.csh\n" )
    write.write( "run_netlist_postprocessing.csh\n" )
    write.write( "touch DONE\n" )
    write.write( "exit\n" )

    write.close()

    os.chmod( "run.csh", stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

    command = "bsub -q normal " + gWorkingDirectory + "/database/run.csh"

    write = open( "job.id", "w" )

    subprocess.call( command, shell = True, stdout = write, stderr = write )

    write.close()

    flag = gWorkingDirectory + "/database/DONE"

    while not os.path.exists( flag ):
      time.sleep( 60 )

    job = ""

    with open( "job.id", "r" ) as read:
      for line in read.readlines():
        matchObjects = re.match( r'^\s*Job <(\d+)> is submitted to queue <\S+>\.', line )
      if matchObjects:
        job = matchObjects.group( 1 )

    write = open( "auto_kill", "w" )

    subprocess.call( "bkill " + job, shell = True, stdout = write, stderr = write )

    write.close()

# V0/check/    Running to check in subdirectoris of V0
  runChecks = list()

  for check in checks:
    flag = gWorkingDirectory + "/" + check + "/DONE"

    if ( not os.path.exists( flag ) \
         or \
         ( "rerun" in arguments.keys() and check in arguments[ "rerun" ] ) \
       ):
      runChecks.append( check )

  if len( runChecks ) > 0:

    for check in runChecks:

      print( "[INFO] START CHECK %s..." % ( check ) )

      os.chdir( gWorkingDirectory + "/" + check + "/" )

      command = "bsub -q drc " + gWorkingDirectory + "/" + check + "/run.csh"

      write = open( "job.id", "w" )

      subprocess.call( command, shell = True, stdout = write, stderr = write )

      write.close()

    for check in runChecks:
      flag = gWorkingDirectory + "/" + check + "/DONE"

      while not os.path.exists( flag ):
        time.sleep( 60 )

# database/   Write run_write_excel.csh and run it, to generate CSV and Excel.
  print( "[INFO] WRITE TO EXCEL" )

  currentCheck = ""
  previousCheck = ""

  if ( arguments[ "preVersion" ][ 0 ] != "" \
       and \
       os.path.exists( root + "/" + arguments[ "preVersion" ][ 0 ] + "/" ) \
     ):
    previousCheck = root + "/" + arguments[ "preVersion" ][ 0 ] + "/"

  if os.path.exists( root + "/" + arguments[ "version" ][ 0 ] + "/" ):
    currentCheck = root + "/" + arguments[ "version" ][ 0 ] + "/"

  os.chdir( gWorkingDirectory + "/database/" )

  write = open( "run_write_excel.csh", "w" )

  write.write( "#!/bin/csh -f\n" )
  write.write( "\n" )
  write.write( "set createCSV = %s\n" % ( gDesignSignoffCheckCSVCreationPath ) )
  write.write( "set createExcel = %s\n" % ( gDesignSignoffCheckCSVtoExcelPath ) )
  write.write( "${createCSV} \"%s\" \"%s\" \"Summary.csv\"\n" % ( previousCheck, currentCheck ) )
  write.write( "${createExcel} \"Design_Signoff_PERC_Check_Result_with_Circuit_Version_%s.xlsx\" \"Summary.csv\"" % ( arguments[ "version" ][ 0 ] ) )
  #No "\n"
  for check in checks:
    write.write( " \"%s\"" % ( re.sub( r'_', "", check ) + ".csv" ) )

  write.write( "\n" )
  write.write( "exit\n" )

  write.close()

  os.chmod( "run_write_excel.csh", stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

  command = gWorkingDirectory + "/database/run_write_excel.csh"

  subprocess.call( command, shell = True, stdout = None, stderr = None )

# V0/check/  Print calibre and comparision check results.
  for check in checks:

    calibreState = "[ABORT]"
    comparisonState = "[ABORT]"

    os.chdir( gWorkingDirectory + "/" + check + "/" )

    if os.path.exists( "perc.rep" ):
      read = open( "perc.rep", "r" )

      for line in read.readlines():

        matchObjects = re.match( r'^\s*#\s+CHECK\(s\)\s+(\S+)\s+#', line )

        if matchObjects:

          if matchObjects.group( 1 ) == "PASSED":
            calibreState = "[PASS]"

          elif matchObjects.group( 1 ) == "FAILED":
            calibreState = "[FAIL]"

          break

      read.close()

    if os.path.exists( "summary.rpt" ):
      comparisonState = "[OK]"

    print( "" )
    print( "[INFO] CHECK \"%s\" STATUS" % ( check ) )
    print( "         CALIBRE ......... %s" % ( calibreState ) )
    print( "         COMPARISON ...... %s" % ( comparisonState ) )

# Write run_combine_wesign_summary.csh and run it in database directory , to generate *./rpt files in subdirectories of V0.
  os.chdir( gWorkingDirectory + "/database/" )

  write = open( "run_combine_wesign_summary.csh", "w" )

  write.write( "#!/bin/csh -f\n" )
  write.write( "\n" )
  write.write( "set wesign = \"" + gDesignSignoffCheckResultForWesignCSV + "\"\n" )
  write.write( "${wesign}" )

  for check in checks:
    write.write( " " + gWorkingDirectory + "/" + check + "/wesign_summary.rpt" )

  write.write( "\n" )
  write.write( "exit\n" )

  write.close()

  os.chmod( "run_combine_wesign_summary.csh", stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH + stat.S_IXOTH )

  command = gWorkingDirectory + "/database/run_combine_wesign_summary.csh"

  subprocess.call( command, shell = True, stdout = None, stderr = None )

  sys.exit( 0 )
