#!/system/bin/sh
# Tool to extract and set up Android Python on the target system
# DO NOT RUN THIS ON YOUR COMPUTER; IT WILL NOT WORK

echo $(uname -m)
echo $(whoami)
py_prefix=python$1 # avoid nasty input errors deleting/overwriting /system/lib/
echo $py_prefix

# Make sure we're in the right directory
cd /data/local/tmp

# We need to move the executable out of the way first, since it's only called 'python3.9'
# Otherwise, this file would conflict with the directory created when we extract
# the libraries
echo "Installing executable"
mv -f -v ${py_prefix} /system/bin/${py_prefix}
# create symlinks
maj_version=$(echo ${py_prefix} | sed -r 's/(python[0-9]+)\..*/\1/')
ln -sf /system/bin/${py_prefix} /system/bin/${maj_version} # pythonX -> pythonX.Y
ln -sf /system/bin/${py_prefix} /system/bin/python         # python  -> pythonX.Y

echo "Extracting archive"
gzip -c -d ${py_prefix}.tar.gz | tar -x # Should create a directory ${py_prefix}/
if [ $? != 0 ]; then
  echo "Failed to extract archive"
  exit 1
fi

if [ -e /system/lib/${py_prefix} ]; then
  echo "Removing old Python installation"
  rm -r /system/lib/${py_prefix}
fi

# mv probably has to move the extracted files to a different filesystem
# this requires a copy-delete and is much slower than just renaming
echo "Installing python libraries"
mv ${py_prefix} /system/lib

rm ${py_prefix}.tar.gz

echo "Install completed successfully!"
echo "Run 'python' in an ADB shell to make sure everything works."
