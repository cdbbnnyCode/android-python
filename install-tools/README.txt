Android-Python for the REV Control Hub
Copyright (C) 2021 Aidan Yaklin
This project is licensed under the MIT license. See
https://github.com/cdbbnnyCode/android-python/blob/master/LICENSE.txt for more details.

HOW TO USE
* Connect your REV hub to your computer with ADB (Wifi or USB should work, as long
as it's connected.)
* Make sure that ADB (the Android Debugger) is in your PATH. This tool comes with
Android Studio and is usually located in
<user home folder>/Android/Sdk/platform-tools or
<user home folder>/AppData/Local/Android/Sdk/platform-tools.
* Open up a terminal/command line and run
 python install.py
Double-clicking install.py in Windows *might* also work, but this hasn't been tested.
* When prompted, type 'yes' to confirm the installation.
* Once the installation is finished, test it by opening an ADB shell with 'adb shell'
and running python. You should be able to import most built-in libraries without
any issues.
