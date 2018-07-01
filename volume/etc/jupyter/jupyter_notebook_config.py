# Configuration file for jupyter-notebook.

import os
from IPython.lib import passwd

c = get_config()
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = int(os.getenv('JUPYTER_PORT', 8888))
c.NotebookApp.open_browser = False
c.NotebookApp.notebook_dir = '/root'
c.NotebookApp.base_url = os.getenv("JUPYTER_BASEURL", "/")
c.NotebookApp.iopub_data_rate_limit=100000000.0 #(bytes/sec)
c.NotebookApp.rate_limit_window=10.0 #(secs)

# sets a password if JUPYTER_PASSWORD is set in the environment
if 'JUPYTER_PASSWORD' in os.environ:

  #c.NotebookApp.token = passwd(os.environ['JUPYTER_TOKEN'])
  c.NotebookApp.password = passwd(os.environ['JUPYTER_PASSWORD'])
  del os.environ['JUPYTER_PASSWORD']

print("jupyter config..")
print(c)
