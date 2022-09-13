@ECHO off

SET installerpath=%~dp0
SET initpath=%installerpath%maya_init.py
SET "initpath=%initpath:\=/%"
SET mayascriptpath="%USERPROFILE%\My Documents\maya\2020\scripts\"
SET usersetupfile=%mayascriptpath%userSetup.py
SET pythonstring=execfile^('%initpath%'^)

echo. 2>%usersetupfile%
@echo %pythonstring%>%usersetupfile%

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
SET mayaversionpath="%USERPROFILE%\My Documents\maya\2020\"
SET mayaenvfile=%mayaversionpath%Maya.env

REM Write all these variables to the Maya.env file
echo. 2>%mayaenvfile%
echo %bifrostcmd%>>%mayaenvfile%
echo %mayamodulepathcmd%>>%mayaenvfile%
echo %mgearshifterpathcmd%>>%mayaenvfile%
echo %mgearcustomstepspathcmd%>>%mayaenvfile%
