!define py2exeOutputDir 'dist'
!define exe             'main.exe'
!define icon            'icon/dm.ico'
!define compressor      'lzma'  ;one of 'zlib', 'bzip2', 'lzma'
!define outExe          'DMIDE.exe'
!define onlyOneInstance

; - - - - do not edit below this line, normaly - - - -
!ifdef compressor
    SetCompressor ${compressor}
!else
    SetCompress Off
!endif
Name ${exe}
OutFile ${outExe}
SilentInstall silent
!ifdef icon
    Icon ${icon}
!endif

; - - - - Allow only one installer instance - - - - 
!ifdef onlyOneInstance
Function .onInit
 System::Call "kernel32::CreateMutexA(i 0, i 0, t '$(^Name)') i .r0 ?e"
 Pop $0
 StrCmp $0 0 launch
  Abort
 launch:
FunctionEnd
!endif
; - - - - Allow only one installer instance - - - - 

Section
    InitPluginsDir
    SetOutPath '$PLUGINSDIR'
    File /r '${py2exeOutputDir}\*.*'
    SetOutPath '$EXEDIR'        ; uncomment this line to start the exe in the PLUGINSDIR
    nsExec::Exec $PLUGINSDIR\${exe}
SectionEnd