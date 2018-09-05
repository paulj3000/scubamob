#!/home/pauldim1/python/bin/python

import os,sys

# Activate your virtual env
activate_env=os.path.expanduser("/home/pauldim1/public_html/scubamob/current/smenv/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

sys.path.insert(0, '/home/pauldim1/public_html/scubamob/current')

os.environ['DJANGO_SETTINGS_MODULE'] = 'scuba.settings'

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
