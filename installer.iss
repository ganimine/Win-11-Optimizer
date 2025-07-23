; Inno Setup script for Windows 11 Optimizer App
; Save this as installer.iss and open with Inno Setup Compiler

[Setup]
AppName=Windows 11 Optimizer
AppVersion=1.0
DefaultDirName={pf}\Windows11Optimizer
DefaultGroupName=Windows 11 Optimizer
OutputDir=dist
OutputBaseFilename=Windows11OptimizerSetup
Compression=lzma
SolidCompression=yes

LicenseFile=license.txt
WizardImageFile=wizard.bmp
WizardSmallImageFile=smallwizard.bmp

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Windows 11 Optimizer"; Filename: "{app}\main.exe"
Name: "{userdesktop}\Windows 11 Optimizer"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\main.exe"; Description: "Launch Windows 11 Optimizer"; Flags: nowait postinstall skipifsilent
