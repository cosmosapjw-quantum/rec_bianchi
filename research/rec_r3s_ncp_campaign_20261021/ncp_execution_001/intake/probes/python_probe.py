import importlib.metadata as im, json, platform, sys
import numpy as np, scipy, pytest
try:
 from threadpoolctl import threadpool_info
 pools=threadpool_info()
except Exception as e:
 pools={"status":"unavailable","error":type(e).__name__+":"+str(e)}
a=np.array([1.0,2.0],dtype=np.float64); b=np.array([2.0,1.0],dtype=np.float64)
assert float(a@b)==4.0
print(json.dumps({"status":"PYTHON_PASS","python":sys.version,"executable":sys.executable,"platform":platform.platform(),"numpy":np.__version__,"numpy_file":np.__file__,"scipy":scipy.__version__,"pytest":pytest.__version__,"probe_result":float(a@b),"threadpools":pools},sort_keys=True))
