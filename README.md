# cache_manager
Tool using Houdini to handle local caching
This is made using python3 as python 2.7 is now deprecated and won't be updated anymore

## Description
This tool is a cache manager. This will allows you to start your caches without opening Houdini as if you were using the command line.

## Prerequisites
This has been tested only on Windows 10 while using Houdini python3 build (we can't use PySide2 in Windows unless you compile it).
PySide2
QtPy


### Installation
You will need to add the path of the \bin folder to the Windows System variable variable.
This should look like this:
```
C:\Program Files\Side Effects Software\Houdini 18.0.502_Py3\bin
```

Once you have done that, create a houdini_module.pth file and put it inside the site-packages of your python install.
To find out where your python is, open a shell and type:
```
where python
```
 
Then, you must tells python where the hou module is located. I found the easiest way to do without touching too much to the environment variables was to use a .pth file. This file will be place inside the pyton\lib\site-packages folder. 
The default installation of python is there: C:\users\<USER>\Local Settings\Application Data\Programs\Python\Python37

We will now install PySide2 to handle the UI of the tool.
For that, type "pip install PySide2" ad also that: "pip install qtpy". If you want more information on PySide, you can go to this page: https://pypi.org/project/PySide2/
There is also a theme that I used to get a frameless window, to get it use this: "pip install qtmodern". For more information on this theme, you can go check this page: https://github.com/gmarull/qtmodern

