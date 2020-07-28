# cache_manager
Tool using Houdini to handle local caching
This is made using python3 as python 2.7 is now deprecated and won't be updated anymore

## Description
This tool is a cache manager. This will allows you to start your caches without opening Houdini as if you were using the command line.

## Prerequisites
This has been tested only on Windows 10 while using Houdini python3 build (we can't use PySide2 in Windows unless you compile it).
**YOU WILL NEED A HOUDINI PYTHON3 BUILD TO HAVE THIS PROJECT WORKING**

Here are the pythons modules needed for this to work
* PySide2 (https://wiki.qt.io/Qt_for_Python)
* qtpy (https://pypi.org/project/QtPy/)
* qtmodern (https://github.com/gmarull/qtmodern)

To install PySide2, we will use pip which is the package Installer for Python.
You will have to open a new shell, and type
```
pip install PySide2
```

Same thing for qtpy, in this same shell, you will need to type:
```
pip install qtpy
```

Finally, to get a good looking interface, install qtmodern like that:
```
pip install qtmodern
```

### Installation
You will need to add the path of the \bin folder to the Windows System variable variable.
This should look like this:
```
C:\Program Files\Side Effects Software\Houdini 18.0.502_Py3\bin
```

Once you have done that, create a houdini_module.pth file or use the provided one and put it inside the site-packages of your python install.
To find out where your python is, open a shell and type:
```
where python
```
This will allows Python to find the Houdini python module

### How to run the script
To run the script, go with a shell to the folder where you put your downloaded script and in a shell:
```
python main.py
```
To have this working, python must be inside your PATH System variables 
