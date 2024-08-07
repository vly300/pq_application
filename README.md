Introduction

Parliamentary Questions (PQs) are questions which MSPs submit to obtain information and data relevant to their duties.

This application allows for the retrieval and collation of the PQs into one space, so users can have a consistently available source to access the PQs, and also self-allocated PQs when appropriate.
This application also provides for Admin level users (Stats Gov members) to efficiently store the PQs, and sort it out using various automated features. 

The Python scripts were created using Visual Studio Code, within a virtual environment running Python 3.10.11.

The UI files were created in Qt Designer, which is a UI to create the UI.

To access and run the files, you should:

- Create a virtual environment
- install pyqt5 (this gives the packages to run the functions in Python)
- install pyqt5-tools (this gives access to the Qt Designer)

Designer app is found in:
\venv\Lib\site-packages\qt5_applications\Qt\bin\designer

You can also convert the UI files to Python files:

In cmd, run:
project_location\venv\Scripts\activate
project_location\GUI_files

then run `pyuic5 -x insert_file_name.ui -o insert_file_name.py`
