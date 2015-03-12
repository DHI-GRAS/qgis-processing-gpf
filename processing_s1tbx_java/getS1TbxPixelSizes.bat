@ECHO OFF

set NEST_HOME=%~1
set CODE_HOME=%~dp0

cd /D %CODE_HOME%

"%NEST_HOME%\jre\bin\java.exe" ^
-Xmx1024M ^
-cp ^
"%NEST_HOME%lib\*;^
%NEST_HOME%modules\*;" getS1TbxPixelSizes %2 %3

exit /B 0