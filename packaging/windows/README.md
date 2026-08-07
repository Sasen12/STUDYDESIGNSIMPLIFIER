# Windows installer

This directory contains the Inno Setup configuration for the Windows installer.

## Build on Windows

Install Flutter, Visual Studio with **Desktop development with C++**, and Inno
Setup. From the repository root, run:

```powershell
flutter pub get
flutter build windows --release
```

Then open `packaging/windows/vce_unpacked.iss` in Inno Setup and choose
**Build > Compile**. The installer will be written to:

```text
packaging/windows/output/VCEUnpackedSetup.exe
```

The installed application defaults to:

```text
C:\Program Files\VCE Unpacked\
```

The installer includes the complete Flutter release directory, including the
application executable, DLLs, and bundled study data.

## Build without using Flutter locally

The repository also includes a GitHub Actions workflow:

```text
.github/workflows/build-windows-installer.yml
```

On GitHub, open **Actions**, select **Build Windows installer**, choose **Run
workflow**, and wait for it to finish. Download the artifact named
`VCEUnpacked-Windows-Installer` and send the resulting
`VCEUnpackedSetup.exe` to the recipient.

The recipient only needs to double-click the installer. They do not need
Flutter, Python, Visual Studio, or any command-line knowledge.

## GitHub Releases

The workflow at `.github/workflows/release-installers.yml` builds both
installers whenever a GitHub Release is published. The release will contain:

```text
VCEUnpackedSetup.exe
VCEUnpacked.dmg
```

Create a release from a version tag such as `v1.0.0`; the two platform builds
will be attached automatically.
