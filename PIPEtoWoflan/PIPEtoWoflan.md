This module converts XML and CPN files containing Petri net descriptions to a TPN file containing a Petri net description. It allows for more than one file to be input at a time, as long as they are in a single, one-level folder (meaning it ignores child folders).

It has dependencies on bs4, lxml and PySimpleGUI. bs4 and lxml allow us to navigate the XML and CPN (which is also formatted as a XML file) files; PySimpluGUI is used to provide a more user-friendly interface with which to work with the module.

Some of those packages have their own requirements, as follows:

- bs4 requires beautifulsoup4, which requires soupsieve.
- PySimpleGUI requires tkinter.

The module allows as an input parameter an empty list of files, but must have an output location specified. This is by design.

WARNING: This module overwrites any file with the same name as the outputs (which are the names of the original files with .tpn extension).
