; Inno Setup installer for VCE Study Tracker.
; Build the Flutter release first:
;   flutter build windows --release
; Then open this file in Inno Setup and choose Build > Compile.

#define MyAppName "VCE Study Tracker"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "VCE Study Tracker"
#define MyAppExeName "vce_study_tracker.exe"
#define ReleaseDir "..\\..\\build\\windows\\x64\\runner\\Release"

[Setup]
AppId={{B8F0C2B7-5BE4-4C7C-AF5A-7C2F56FD6B8A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\VCE Study Tracker
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=VCEStudyTrackerSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "{#ReleaseDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
