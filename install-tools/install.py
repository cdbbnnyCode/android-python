import os
import sys
import subprocess
import json

def run(*command, cwd=None):
    print(command)
    try:
        result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE)
        return result.returncode, result.stdout.decode('utf-8').strip()
    except OSError:
        return 127, []

def main():
    r, stdout = run('adb', 'devices')
    if r != 0:
        print("Failed to run adb. Make sure it is in your PATH?")
        print("hint: adb is in <Android SDK dir>/platform-tools/")
        sys.exit(1)
    if len(stdout.split('\n')) < 2:
        print("No devices found. Make sure you are connected to your REV hub over")
        print("USB or WiFi.")
        sys.exit(0)

    if not os.path.exists('install.txt'):
        print("Could not find 'install.txt'. Did you mean to run build.py instead?")
        print("This file should only be used inside an install archive directory.")
        sys.exit(1)

    with open('install.txt', 'r') as f:
        install_info = json.load(f)

    python = install_info['python']
    version = install_info['version']

    print("This tool will install Python v%s onto your REV Control Hub. This requires" % version)
    print("uploading files into the hub's system folders.")
    print()
    print("-- USE AT YOUR OWN RISK! However, if this 'bricks' your Control Hub, you should")
    print("be able to re-install the Control Hub OS with the REV Hardware Client.")
    print()
    print("-- If you are using Blocks or OnBot Java, consider backing up the files on your")
    print("Control Hub before continuing.")
    print()
    print("Type 'yes' to continue: ", end="")
    resp = input()
    if resp != 'yes':
        print("Nope!")
        sys.exit(0)

    print("Rooting REV hub...")
    r, stdout = run('adb', 'root')
    if r != 0:
        print("Root failed")
        sys.exit(1)

    r, stdout = run('adb', 'remount')
    if r != 0:
        print("Remount failed")
        sys.exit(1)

    print("Uploading python...")
    version_maj = version.split('.')[0]
    r, stdout = run('adb', 'push', python, '/system/bin/')
    if r != 0:
        print("Upload failed")
        sys.exit(1)

    print("Uploading python libraries...")
    r, stdout = run('adb', 'push', python + '.tar.gz', '/data/local/tmp')
    if r != 0:
        print("Upload failed")
        sys.exit(1)

    print("Uploading install script...")
    r, stdout = run('adb', 'push', 'install.sh', '/data/local/tmp')
    if r != 0:
        print("Upload failed")
        sys.exit(1)

    print("Running install script...")
    r, stdout = run('adb', 'shell', 'chmod', '755', '/data/local/tmp/install.sh')
    if r != 0:
        print("chmod failed")
        sys.exit(1)
    r, stdout = run('adb', 'shell', '/data/local/tmp/install.sh', python[len('python'):])

    if r != 0:
        print("Installation failed!")
        print("There are still temporary files in /data/local/tmp. Make sure to")
        print("delete them (in the Android Studio Device File Explorer).")
        sys.exit(1)
