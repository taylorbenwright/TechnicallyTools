@ECHO off

SET installerpath=%~dp0
SET initpath=%installerpath%maya_init.py
SET "initpath=%initpath:\=/%"
SET mayascriptpath="%USERPROFILE%\My Documents\maya\2022\scripts\"
SET usersetupfile=%mayascriptpath%userSetup.py

SET ps1=def execfile^(filepath,globals=None,locals=None^):
SET ps2=    if globals is None:
SET ps3=        globals={}
SET ps4=    globals.update^({"__file__":filepath,"__name__":"__main__"}^)
SET ps5=    with open^(filepath,'rb'^) as f:
SET ps6=        exec^(compile^(f.read^(^),filepath,'exec'^),globals,locals^)
SET ps7=execfile('%initpath%')

echo. 2>%usersetupfile%
@echo %ps1%>%usersetupfile%
@echo %ps2%>>%usersetupfile%
@echo %ps3%>>%usersetupfile%
@echo %ps4%>>%usersetupfile%
@echo %ps5%>>%usersetupfile%
@echo %ps6%>>%usersetupfile%
@echo %ps7%>>%usersetupfile%

REM Set up Bifrost path
SET bifrostpath=%installerpath:MayaEnv\bootstrap\=Bifrost\TGConfiguration.json%
SET bifrostcmd=BIFROST_LIB_CONFIG_FILES^=%bifrostpath%

REM Set up Module path
SET mayamodulepath=%installerpath:MayaEnv\bootstrap\=Modules%
SET mayamodulepathcmd=MAYA_MODULE_PATH^=%mayamodulepath%

REM Set up mGear paths
SET mgearshifterpath=%installerpath:MayaEnv\bootstrap\=MayaEnv\mgear\modules%
SET mgearshifterpathcmd=MGEAR_SHIFTER_COMPONENT_PATH ^=%mgearshifterpath%

SET mgearcustomstepspath=%installerpath:MayaEnv\bootstrap\=MayaEnv\mgear\custom_steps%
SET mgearcustomstepspathcmd=MGEAR_SHIFTER_CUSTOMSTEP_PATH ^=%mgearcustomstepspath%

REM Get Maya.env path
SET mayaversionpath="%USERPROFILE%\My Documents\maya\2022\"
SET mayaenvfile=%mayaversionpath%Maya.env

REM Write all these variables to the Maya.env file
echo. 2>%mayaenvfile%
echo %bifrostcmd%>>%mayaenvfile%
echo %mayamodulepathcmd%>>%mayaenvfile%
echo %mgearshifterpathcmd%>>%mayaenvfile%
echo %mgearcustomstepspathcmd%>>%mayaenvfile%
