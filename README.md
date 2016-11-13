# MK8-Editor
An editor for the WiiU game, Mario Kart 8. It currently only edits course BYAMLs, which contain info about the objects in courses.

**IMPORTANT: I did not make this editor. It was originally a fork of [Kinnay's SM3DW Editor](https://github.com/Kinnay/SM3DW-Level-Editor), which was then modded by Mr. Rean among other people to edit MK8. I, TheKoopaKingdom, just made tweaks to Mr. Rean's editor, whose Github has been nuked.**

## Setup
This requires the following:
 - **A dump of Mario Kart 8's files** - This is what MK8-Editor operates on, you can get them with [ddd](https://gbatemp.net/threads/ddd-wiiu-title-dumper.418492/). ddd is a Wii U application for the [Homebrew Launcher](https://gbatemp.net/threads/homebrew-launcher-for-wiiu.416905/). You can use it by extracting ddd and the Homebrew Launcher's files to an SD card, putting that in your Wii U, going to http://loadiine.ovh/, and selecting Homebrew Launcher RC1.
 - **Python 2.7 32-bit** - Go [here](https://www.python.org/downloads/), and click Download Python 2.7.11. Install it to C:\Python27. You can keep the default settings, but adding python.exe to your path will make things easier later on.
 - **PyQt4** - Go [here](https://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/), click PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x32.exe, and run the installation. If it complains about not having Python, confirm that you are on a 32-bit version of Python (We use this because of PyOpenGL), and that you are on version 2.7.11.
 - **PyOpenGL** - Open a command prompt (Search for cmd.exe). If this is the first time you've installed any version of Python, type **pip install PyOpenGL**. If you have multiple installations of Python on your computer, type **C:\Python27\Scripts\pip.exe install PyOpenGL**.
 - **A hex editor** - [HxD](https://mh-nexus.de/en/downloads.php) will do.

This application uses Python 2.7, and not 3.5, so type **python -V** into a command promt.
If it outputs anything other than Python 2.7.11, you'll run launch.bat.

If running **python -V** did output Python 2.7.11, you should be able to double click on main.py and be fine.

## Usage
This tool edits course BYAML files, you can find one in your MK8 files using [this reference](https://docs.google.com/spreadsheets/d/1CiijrS6P6gqLAfzqKQLpZGd-CeljqzuDFvfLg6ThW3A/). Due to a bug in saving, before doing anything, open your BYAML in a hex editor and copy the first row of bytes (Offset 0x00000000-0x0000000F) paste it somewhere for later.

After making your changes and saving the file from MK8-Editor, open up the new BYAML in a hex editor and paste the bytes we copied earlier to offset 0x00000000.
