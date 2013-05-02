Zem

Zem is an implementation of Casey Duncan's excellent External Editor
for Mac OS X, providing Mac users with flexibility in their choice of
content-specific editors, and as many concurrent editors as they need
running at the same time.

Taking Casey's work, and adapting it for Mac OS X users using the
PyObjC bridge, I provide the same functionality, but in a native Mac
OS X application with an intuitive graphical user interface. This
means that you can specify any Mac OS X application (Carbon or Cocoa)
to act as the editor for a MIME type, type group, or Zope
meta_type. And you can have as many concurrent edits as you like,
since all edits are handled through Zem.

Installing It

Drag the ZopeEditManger application to the Applications folder in your
hard drive or home directory. You can use the built-in preferences,
one of the supplied preference files, or edit your own.

Using It

As you download links from the Zope Management Interface (ZMI) or the
Content Management Framework (CMF) or Plone, new documents will
accumulate in the main table.

As saves are made in the editor, Zem will synch those changes back to
the server, and display the time of the last synch. To remove a
document from Zem, simply select it from the table, and click the
'Finish' button, or press the 'delete' key.

Configuring your Browser

Currently, the only browser fully set to work with Zem is
Mozilla. Internet Explorer supports the configuration of File Helpers,
but I've been unable to get it working quite right. In any case, other
browsers will download a particular file. That file can be dragged
onto the Zem icon and it will work fine. To enable Zem in Mozilla,
select the Helper Applications pane from the Navigator group, and
create a New Type called 'application/x-zope-edit', and choose Zem
with the Application picker.

Configuration

Zem provides a GUI Preferences panel. Just choose "Preferences..."
from the Zem menu, or press Command-, to open the window.

Options

The available options for Zem are (names in parentheses are the
corresponding key names in the Preferences plist):

Files Prefs

Cleanup Files (cleanup_files)

    Whether to delete the temp files created.

    WARNING the temp file coming from the browser contains
    authentication information and therefore setting this to <false/>
    is a security risk, especially on shared machines. If set to
    <true/>, that file is deleted at the earliest opportunity, before
    the editor is even spawned. Set to <false /> for debugging only.

Confirm on Finish (confirm_on_finish)

    When you are finished locally editing a file, Zem will ask you to
    confirm this. You can disable this behavior by unchecking this
    button.

Save Interval (save_interval)

    The interval in seconds that the helper application checks the
    edited file for changes.

Temporary Files (temp_dir)

    Path to store local copies of object data being edited. Defaults
    to /tmp (/ private/tmp).

WebDAV Prefs

Use WebDAV Locks (use_locks)

    Whether to use WebDAV locking. The user editing must have the
    proper WebDAV related permissions for this to work.

Always borrow WebDAV Locks (always_borrow_locks)

    When use_locks is enabled this features suppresses warnings when
    trying to edit an object you have already locked. When enabled,
    external editor will always "borrow" the existing lock token
    instead of doing the locking itself. This is useful when using
    CMFStaging for instance. If omitted, this option defaults to
    <false/>.

Helper Apps Prefs

To edit an entry, simply double click on the cell, and edit. To add a
new Helper App, click the '+' button. To remove an entry, select a
row, and click '-'. You can sort the table by any of the columns,
ascending or descending.

Type

    Either the meta_type of the Zope object, or the MIME type of the
    file it would represent.

Extension (extension)

    The file extension to add to the content file. Allows better
    handling of images and can improve syntax highlighting.

Editor (editor)

    Application name used to invoke the editor application.

Credits

I would like to thank the following people for their help in this
endeavor:

  - Casey Duncan, for the excellent ExternalEditor product, and the
    initial zopeedit.py

  - Bill Bumgarner and Bob Ippolito, for their hard work on PyObjC,
    and their endless help on #macpython on irc.freenode.net.

  - Jesus Diaz Blanco, for his help refining the UI

  - Sascha Gresk, Eric W. Brown, Brian Morton, Jeff Putsch, Aurelius
    Prochazka, Jurgen Valldorf, Michael Bond, Sebastien Verbois, Jonah
    Crawford, Jean-Philippe Rey, Jim Allman, and Alan Runyan for using
    it and supplying valuable feedback

Conclusion

I hope you enjoy using this software. If you have any comments,
suggestions or would like to report a bug, send an email with 'Zem' in
the Subject line to the author:

Zachery Bir <zbir@urbanape.com>

(C) 2003-2005, Zachery Bir and Zope Corporation. All rights reserved.

