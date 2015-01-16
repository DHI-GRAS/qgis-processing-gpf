@ECHO OFF

set BEAM4_HOME=%~1
set CODE_HOME=%~dp0

cd /D %CODE_HOME%

"%BEAM4_HOME%\jre\bin\java.exe" ^
-Xmx1024M ^
-cp ^
"%BEAM4_HOME%lib\*;^
%BEAM4_HOME%bin\*;^
%BEAM4_HOME%modules\*;" listBeamBands %2 %3 %4

exit /B 0