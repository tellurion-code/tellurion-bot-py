import pickle
import os.path
from subprocess import call
def saveObject(object, objectname):
    with open("tmp/" + objectname, "wb") as pickleFile:
        pickler = pickle.Pickler(pickleFile)
        return unpickler.dump(object)

def loadObject(objectname):
    if saveExists(objectname):
        with open("tmp/" + objectname + "tmp", "wb") as pickleFile:
            unpickler = pickle.Unpickler(pickleFile)
            return unpickler.load()
        call(['mv', "tmp/" + objectname + "tmp", "tmp/" + objectname])

def saveExists(objectname):
    return os.path.isfile("tmp/" + objectname)
