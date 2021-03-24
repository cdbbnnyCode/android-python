#!/usr/bin/env python3

import subprocess
import sys
import os
import shutil
import json
import time

def run(*command, cwd=None):
    print(command)
    try:
        result = subprocess.run(command, cwd=cwd)
    except OSError:
        return 127, []
    return result.returncode, "" # TODO

def read_properties(fname):
    data = {}
    with open(fname, 'r') as f:
        for line in f:
            fields = [x.strip() for x in line.split('=')]
            data[fields[0]] = fields[1]
    return data

def check_git():
    rcode, stdout = run('git', '--version')
    return rcode == 0

def check_python():
    if os.path.exists('python'):
        if not os.path.isdir('python'):
            return 1
        else:
            if os.path.exists('python/.git'):
                return 2
            else:
                return 1
    else:
        return 0

def check_ndk(ndk_dir, min_ver, checking_sub=False):
    if not os.path.exists(ndk_dir):
        return 1
    if os.path.exists(ndk_dir + '/source.properties'):
        info = read_properties(ndk_dir + '/source.properties')
        if not 'Pkg.Revision' in info:
            return 1
        vn = [int(x) for x in info['Pkg.Revision'].split('.')]
        for i in range(len(vn)):
            if i >= len(min_ver):
                print('versions equal')
                return 0
            elif vn[i] > min_ver[i]:
                print('later version')
                return 0
            elif vn[i] < min_ver[i]:
                print('earlier version')
                return 1
        print('versions equal')
        return 0
    else:
        return 1

def trymkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        return 0
    elif not os.path.isdir(dir):
        print("'%s' exists and is a file. Please move or delete it." % dir)
        return 1
    else:
        return 0

def copy(src, dest):
    print("%s -> %s" % (src, dest))
    shutil.copy(src, dest)

def main():
    start_time = time.perf_counter()
    print("Building Python for Android 24 64-bit ARM (aarch64-linux-android)")
    print("Checking/installing dependencies")

    # TODO arguments
    py_version='v3.9.2'
    ndk_dir=os.getenv('HOME') + '/Android/Sdk/ndk/22.0.7026061'
    ndk_min_ver=(22,)
    make_jobs=6
    target='aarch64-linux-android'
    android_ver='24'
    shell='/usr/bin/bash'
    make='/usr/bin/make'
    tar='/usr/bin/tar'
    force_build=False

    if not check_git:
        print("Could not find Git. Is it in your PATH?")
        sys.exit(1)

    res = check_python()
    if res == 1:
        print("'python' is already a file or directory. Please delete or move it.")
        sys.exit(1)
    elif res == 2:
        print("'python' submodule found")
    else:
        rval = run('git', 'submodule', 'update')[0]
        if rval != 0:
            print("Clone failed!")
            sys.exit(2)

    print("Checkout version '%s'" % py_version)
    rval = run('git', '-C', 'python/', 'checkout', py_version)[0]
    if rval != 0:
        print("Checkout failed!")
        sys.exit(2)

    print("Checking NDK")
    if check_ndk(ndk_dir, ndk_min_ver) != 0:
        print("NDK not found. Please install NDK version %s or later and specify --ndk-dir" % ('.'.join(min_ver)))
        sys.exit(1)

    print("Setting up build environment")
    if trymkdir('build') != 0:
        sys.exit(1)
    with open('build/config.site', 'w') as f:
        f.write('ac_cv_file__dev_ptmx=no\n')
        f.write('ac_cv_file__dev_ptc=no\n')

    arguments=[shell, '../python/configure']

    toolchain = ndk_dir + '/toolchains/llvm/prebuilt/linux-x86_64'
    arguments.append('--srcdir=../python')
    arguments.append('--prefix=' + os.path.realpath('out/'))
    arguments.append('--build=x86_64-pc-linux-gnu')
    arguments.append('--host=' + target)
    arguments.append('--disable-ipv6')
    arguments.append('CONFIG_SITE=config.site')
    arguments.append('TOOLCHAIN=' + toolchain)
    arguments.append('TARGET=' + target)
    arguments.append('API=' + android_ver)
    arguments.append('AR='  + toolchain + '/bin/llvm-ar')
    arguments.append('CC='  + toolchain + '/bin/' + target + android_ver + '-clang')
    arguments.append('AS='  + toolchain + '/bin/' + target + android_ver + '-clang')
    arguments.append('CXX=' + toolchain + '/bin/' + target + android_ver + '-clang++')
    arguments.append('LD='  + toolchain + '/bin/ld')
    arguments.append('RANLIB=' + toolchain + '/bin/llvm-ranlib')
    arguments.append('STRIP=' + toolchain + '/bin/llvm-strip')
    arguments.append('READELF=' + toolchain + '/bin/llvm-readelf')
    arguments.append('LD_LIBRARY_PATH=' + toolchain + '/sysroot/usr/lib/' + target + \
                        ':' + toolchain + '/sysroot/usr/lib' + target + '/' + android_ver)

    if not os.path.exists('out/bin') or force_build:
        rval = run(*arguments, cwd='build/')[0]
        if rval != 0:
            print("configure failed (%d)" % rval)
            sys.exit(2)

        rval = run(make, 'clean', cwd='build/')[0]
        if rval != 0:
            print("clean failed (%d)" % rval)
            sys.exit(2)

        rval = run(make, '-j' + str(make_jobs), cwd='build/')[0]
        if rval != 0:
            print("compilation failed (%d)" % rval)
            sys.exit(2)

        rval = run(make, 'install', cwd='build/')[0]
        if rval != 0:
            print("install failed (%d)" % rval)
            sys.exit(2)

    pyver_numbers = py_version[1:].split('.')
    python_executable = 'python' + '.'.join(pyver_numbers[0:2])

    print("Building install archive")
    if trymkdir('install') != 0:
        sys.exit(2)
    if os.path.exists('install'):
        for fname in os.listdir('install'):
            os.remove('install/' + fname)

    copy('out/bin/' + python_executable, 'install/' + python_executable)
    install_archive = 'install/' + python_executable + '.tar.gz'
    if os.path.exists(install_archive):
        os.remove(install_archive)
    run(tar, '-C', 'out/lib', '-cvzf', install_archive, 'python3.9/')

    build_time = time.localtime()

    install_info = {
        'version': py_version[1:],
        'python': python_executable,
        'build-tool-version': '1.0.0',
        'build-date': time.strftime('%Y-%m-%d %H:%M', build_time)
    }

    with open('install/install-info.txt', 'w') as f:
        json.dump(install_info, f)

    # copy install scripts
    copy('install-tools/install.py', 'install/install.py')
    copy('install-tools/install-setup.sh', 'install/install-setup.sh')
    copy('install-tools/README.txt', 'install/README.txt')
    copy('LICENSE', 'install/LICENSE.txt')

    print()
    print("Creating zip archive...")
    output_name = 'android-python-%s-%s' % (py_version, time.strftime('%Y%m%d_%H%M', build_time))
    shutil.make_archive(output_name, 'zip', 'install')
    print("Done! (%.3f s)" % (time.perf_counter() - start_time))
    print()

if __name__ == '__main__':
    main()
