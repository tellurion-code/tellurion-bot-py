import pickle
import os.path
from subprocess import call
def saveObject(object, objectname):
    with open("tmp/" + objectname + "tmp", "wb") as pickleFile:
        pickler = pickle.Pickler(pickleFile)
        pickler.dump(object)
    call(['mv', "tmp/" + objectname + "tmp", "tmp/" + objectname])
def loadObject(objectname):
    if saveExists(objectname):
        with open("tmp/" + objectname, "rb") as pickleFile:
            unpickler = pickle.Unpickler(pickleFile)
            return unpickler.load()

def saveExists(objectname):
    return os.path.isfile("tmp/" + objectname)
