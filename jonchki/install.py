import os
import subprocess


def install_host_debs(astrDeb):
    astrInstall = []
    for strDeb in astrDeb:
        strDpkgStatus = subprocess.check_output(
            "dpkg-query -W -f='${Status}' %s || echo 'unknown'" % strDeb,
            shell=True
        ).decode(
            "utf-8",
            "replace"
        )
        print('Check for %s = %s' % (strDeb, strDpkgStatus))
        if strDpkgStatus != 'install ok installed':
            astrInstall.append(strDeb)
    if len(astrInstall) != 0:
        subprocess.check_call('sudo apt-get update --assume-yes', shell=True)
        subprocess.check_call('sudo apt-get install --assume-yes %s' %
                              ' '.join(astrInstall), shell=True)
