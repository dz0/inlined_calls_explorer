import os

script_dir = os.path.abspath(  os.path.dirname( __file__ ) )

def mypath( path ):
    mypath = os.path.join(script_dir, path) 
    # print("DBG mypath", mypath)
    return mypath
