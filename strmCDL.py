#!/bin/env python3.7
import os,sys,re,traceback

dirScript   = os.path.split(os.path.realpath(__file__))[0]
dirIMCP_pre = dirScript[:dirScript.index("/IMCP/")]
if dirIMCP_pre not in sys.path : sys.path.insert(0,dirIMCP_pre)

from IMCP import *

class strmCDL(object):
      '''
Purpose: strmout CDL
Usage:
      batch  model: strmCDL input.js
      import model: obj=strmCDL(inDict="",cdsLib="",libName="",cellName="",viewName="",model="",cdlName="",runDir="",incFile="")
                    input.js: is a jason file , which is a dict.
                    inDict:   is a dict, as imput.js dict. it is same as the keyword args.

return: obj.cdlName, obj.cdlPath

Notice:
    must given argv:
          cdsLib,libName,cellName,simrc
    option argv:
          inDict: if you give argv by keyName=vale,can not give it.
          viewName: default is schematic
          cdlName : default is schematic
          model   : default is LVS
          runDir  : default is current dir
          incFile : default is empty
'''
      def __init__(self,inDict="",cdsLib="",libName="",cellName="",viewName="",model="",cdlName="",runDir="",incFile="",simrc=""):
         try:
             if inDict:
                keys = inDict.keys()
                if not cdsLib   and "cdsLib"   in keys: cdsLib   = inDict["cdsLib"]
                if not libName  and "libName"  in keys: libName  = inDict["libName"]
                if not cellName and "cellName" in keys: cellName = inDict["cellName"]
                if not viewName and "viewName" in keys: viewName = inDict["viewName"]
                if not model    and "model"    in keys: model    = inDict["model"]
                if not cdlName  and "cdlName"  in keys: cdlName  = inDict["cdlName"]
                if not runDir   and "runDir"   in keys: runDir   = inDict["runDir"]
                if not incFile  and "incFile"  in keys: incFile  = inDict["incFile"]
                if not simrc    and "simrc"    in keys: simrc    = inDict["simrc"]

             if not cdlName : cdlName  = cellName+".cdl"
             if not viewName: viewName = "schematic"
             if not model   : model = "LVS"
             if not runDir  : runDir = os.getcwd() + "/"
             
             runDir = os.path.realpath(runDir) + self.tempDir()
  
             si_env = '''\
simLibName  = "%s"
simCellName = "%s"
simViewName = "%s"
hnlNetlistFileName = "%s"
incFILE = "%s"
''' %(libName,cellName,viewName,cdlName,incFile)
             if model == "LVS":
                si_def = self.envLvs() 
             else:
                print("Can't support CDL model")

             if not os.path.exists(runDir): 
                utPathMakeDir(runDir)
             else:
                utPathCleanDir(runDir)

             utFileWrite(si_env+si_def,runDir+"si.env")

             cmd1 = "/bin/cp -f %s %s.simrc" %(simrc,runDir)      
             cmd2 = "si ./ -cdslib %s -batch -command netlist" %cdsLib
             soa.runCmd(cmd1,cmd2,runDir=runDir,printLog=True)

             print("Run strmout CDL end!")
             self.cdlName = cdlName
             self.cdlPath = runDir+cdlName 

         except Exception as e:
             print("[Error]--in strmout CDL:\n%s" %e)

      def tempDir(self):
          return("/temp_strmCDL/") 

      def envLvs(self):
          rstr = '''
simSimulator = "auCdl"
simNotIncremental = 't
simReNetlistAll = nil
simViewList = '("auCdl" "schematic")
simStopList = '("auCdl")
simNetlistHier = t
resistorModel = ""
shortRES = 0
preserveRES = 't
checkRESVAL = 't
checkRESSIZE = 'nil
preserveCAP = 't
checkCAPVAL = 't
checkCAPAREA = 'nil
preserveDIO = 't
checkDIOAREA = 't
checkDIOPERI = 't
checkCAPPERI = 'nil
simPrintInhConnAttributes = 'nil
checkScale = "meter"
checkLDD = 'nil
pinMAP = 'nil
preserveBangInNetlist = 'nil
shrinkFACTOR = 0.0
globalPowerSig = ""
globalGndSig = ""
displayPININFO = 't
preserveALL = 't
setEQUIV = ""
auCdlDefNetlistProc = "ansCdlSubcktCall"
'''   
          return rstr

if __name__ == "__main__":

  input  = sys.argv[1] if len(sys.argv) >1 else "input.js1" 
  inDict = soa.read(input)
  outCDL = strmCDL(inDict) 


