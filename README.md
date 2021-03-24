# Python For Android

A simple tool to cross-compile and install Python on rooted Android.

### How to install
You can download a pre-compiled installation package from the
[Releases](https://github.com/cdbbnnyCode/android-python/releases) page.
The installation package contains its own instructions.

---
To build from source, you will need:
* Linux: any distro, as long as it has the following:
  * bash
  * make
  * tar
  * git
  * python3
  * An internet connection
  * A few gigs of RAM
* An x86_64 CPU (most PCs these days are x86_64)
* Android Studio, or at least the Android SDK and NDK

You can change configuration options (paths, versions, threads, etc.) in the
`build.py` file (probably somewhere around line 85).

Finally, run `build.py` in a terminal. It will take a few minutes to compile and
will spit out a zip file containing everything you need to install the program.

### Usage
I *will* release a tool for FTC applications to communicate with Python sometime
in the future.

### Uninstallation
* Connect to your REV hub with ADB
* In a terminal, type the following commands to unlock the system directories:
  ```
  adb root
  adb remount
  ```
* In the Android Studio Device File Explorer, delete the following (where X and Y
  are the Python version you have installed):
  ```
  /system/bin/python
  /system/bin/pythonX
  /system/bin/pythonX.Y
  /system/lib/pythonX.Y
  ```
* Run `adb unroot` or reboot the REV hub to re-lock the system files.

### License

This project is
