# cache_manager
Tool using Houdini to handle local caching
This is made using python3 as python 2.7 is now deprecated and won't be updated anymore


This has been tested only on Windows 10 while using Houdini python3 build (we can't use PySide2 in Windows unless you compile it).
To make it work, you will have to add one environment variable to your system and add some modules to python to make it work. If needed, I might make a system which will handle that by itelf.

First, you need to have Houdini\bin in your Path variable. Here is how to do it:
    First, go to your Advanced Systems Parameters -> Environment variables. Under System Variables, select Path and click edit. Add this line and put it first:
  \Houdini_installation_folder\bin DON'T FORGET THAT THIS MUST BE A PYTHON3 HOUDINI BUILD
 
Then, you must tells python where the hou module is located. I found the easiest way to do without touching too much to the environment variables was to use a .pth file. This file will be place inside the pyton\lib\site-packages folder. 
The default installation of python is there: C:\users\<USER>\Local Settings\Application Data\Programs\Python\Python37

We will now install PySide2 to handle the UI of the tool.
For that, type "pip install PySide2" ad also that: "pip install qtpy". If you want more information on PySide, you can go to this page: https://pypi.org/project/PySide2/
There is also a theme that I used to get a frameless window, to get it use this: "pip install qtmodern". For more information on this theme, you can go check this page: https://github.com/gmarull/qtmodern

