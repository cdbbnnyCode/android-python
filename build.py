import subprocess
import sys
import os

def run(*command):
    print(command)
    try:
        result = subprocess.run(command)
    except OSError:
        return 127, []
    return result.returncode, result.stdout.decode('utf-8').strip().split('\n')

def check_git():
    rcode, stdout = run('git', '--version')
    return rcode == 0

def check_python():
    if os.path.exists('python'):
        if not os.path.isdir('python'):
            return 1
        else:
            if os.path.exists('python/.git'):
                return 0
            else:
                return 1
    else:
        return 1

def main():
    print("Building Python for Android 24 64-bit ARM (aarch64-linux-android)")
    print("Checking/installing dependencies")

    if not check_git:
        print("Could not find Git. Is it in your PATH?")
        sys.exit(1)

    
