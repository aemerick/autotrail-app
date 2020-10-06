from flaskapp import app

import os

# this is not great, but for now:
if 'ubuntu' in os.getcwd(): # we are on AWS
    host  = '0.0.0.0'
    debug = False
else:
    host  = '127.0.0.1'
    debug = True

app.run(host = host, debug=debug)
