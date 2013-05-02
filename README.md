<html>
  <head>
    <title>Zem</title>
  </head>
  <body>
    <h1>Zem</h1>

    <p>Zem is an implementation of Casey Duncan's excellent External
      Editor for Mac OS X, providing Mac users with flexibility in
      their choice of content-specific editors, and as many concurrent
      editors as they need running at the same time.</p>

    <p>Taking Casey's work, and adapting it for Mac OS X users using
      the PyObjC bridge, I provide the same functionality, but in a
      native Mac OS X application with an intuitive graphical user
      interface. This means that you can specify any Mac OS X
      application (Carbon or Cocoa) to act as the editor for a MIME
      type, type group, or Zope meta_type. And you can have as many
      concurrent edits as you like, since all edits are handled
      through Zem.</p>

    <h2>Installing It</h2>

    <p>Drag the ZopeEditManger application to the Applications folder
      in your hard drive or home directory. You can use the built-in
      preferences, one of the supplied preference files, or edit your
      own.</p>

    <h2>Using It</h2>

    <p><img src="images/zem_screenshot_1.png" alt=""></p>

    <p>As you download links from the Zope Management Interface (ZMI)
      or the Content Management Framework (CMF) or Plone, new
      documents will accumulate in the main table.</p>

    <p><img src="images/zem_screenshot_2.png" alt=""></p>

    <p>As saves are made in the editor, Zem will synch those changes
      back to the server, and display the time of the last synch. To
      remove a document from Zem, simply select it from the table, and
      click the 'Finish' button, or press the 'delete' key.</p>

    <h2>Configuring your Browser</h2>

    <p>Currently, the only browser fully set to work with Zem is
      Mozilla. Internet Explorer supports the configuration of File
      Helpers, but I've been unable to get it working quite right. In
      any case, other browsers will download a particular file. That
      file can be dragged onto the Zem icon and it will work fine. To
      enable Zem in Mozilla, select the Helper Applications pane from
      the Navigator group, and create a New Type called
      'application/x-zope-edit', and choose Zem with the Application
      picker.</p>

    <p><img src="images/mozilla_config.png" alt=""></p>

    <h2>Configuration</h2>

    <p>Zem provides a GUI Preferences panel. Just choose
      "Preferences..." from the Zem menu, or press Command-, to open
      the window.</p>

    <h2>Options</h2>

    <p>The available options for Zem are (names in parentheses are the
      corresponding key names in the Preferences plist):</p>

    <h3>Files Prefs</h3>

    <p><img src="images/zem_files_prefs.png" alt=""></p>

    <dl>
      <dt>Cleanup Files (<code>cleanup_files</code>)</dt>
      <dd>Whether to delete the temp files created.<br/><br/>WARNING
        the temp file coming from the browser contains authentication
        information and therefore setting this to &lt;false/&gt; is a
        security risk, especially on shared machines. If set to
        &lt;true/&gt;, that file is deleted at the earliest
        opportunity, before the editor is even spawned. Set to
        &lt;false/&gt; for debugging only.</dd>

      <dt>Confirm on Finish (<code>confirm_on_finish</code>)</dt>
      <dd>When you are finished locally editing a file,
        Zem will ask you to confirm this. You can disable
        this behavior by unchecking this button.</dd>

      <dt>Save Interval (<code>save_interval</code>)</dt>
      <dd>The interval in seconds that the helper application checks
        the edited file for changes.</dd>

      <dt>Temporary Files (<code>temp_dir</code>)</dt>
      <dd>Path to store local copies of object data being
        edited. Defaults to /tmp (/private/tmp).</dd>

    </dl>

    <h3>WebDAV Prefs</h3>

    <p><img src="images/zem_webdav_prefs.png" alt=""></p>

    <dl>

      <dt>Use WebDAV Locks (<code>use_locks</code>)</dt>
      <dd>Whether to use WebDAV locking. The user editing must have
        the proper WebDAV related permissions for this to work.</dd>

      <dt>Always borrow WebDAV Locks
        (<code>always_borrow_locks</code>)</dt>
      <dd>When use_locks is enabled this features suppresses warnings
        when trying to edit an object you have already locked.  When
        enabled, external editor will always "borrow" the existing
        lock token instead of doing the locking itself. This is useful
        when using CMFStaging for instance. If omitted, this option
        defaults to &lt;false/&gt;.</dd>

    </dl>

    <h3>Helper Apps Prefs</h3>

    <p><img src="images/zem_helper_apps_prefs.png" alt=""></p>

    <p>To edit an entry, simply double click on the cell, and edit. To
      add a new Helper App, click the '+' button. To remove an entry,
      select a row, and click '-'. You can sort the table by any of
      the columns, ascending or descending.</p>

    <dl>

      <dt>Type</dt>
      <dd>Either the meta_type of the Zope object, or the MIME type of
        the file it would represent.</dd>

      <dt>Extension (<code>extension</code>)</dt>
      <dd>The file extension to add to the content file. Allows better
        handling of images and can improve syntax highlighting.</dd>

      <dt>Editor (<code>editor</code>)</dt>
      <dd>Application name used to invoke the editor application.</dd>

    </dl>

    <h2>Credits</h2>

    <p>I would like to thank the following people for their help in
      this endeavor:</p>

    <ul>

      <li>Casey Duncan, for the excellent ExternalEditor product, and
        the initial zopeedit.py</li>
      <li>Bill Bumgarner and Bob Ippolito, for their hard work on
        PyObjC, and their endless help on #macpython on
        irc.freenode.net.</li>
      <li>Jes&uacute;s D&iacute;az Blanco, for his help refining the
        UI</li>
      <li>Sascha Gresk, Eric W. Brown, Brian Morton, Jeff Putsch,
        Aurelius Prochazka, J&uuml;rgen Valldorf, Michael Bond,
        S&eacute;bastien Verbois, Jonah Crawford, Jean-Philippe Rey,
        Jim Allman, and Alan Runyan for using it and supplying
        valuable feedback</li>

    </ul>

    <h2>Conclusion</h2>

    <p>I hope you enjoy using this software. If you have any comments,
      suggestions or would like to report a bug, send an email with
      'Zem' in the Subject line to the author:</p>

    <p>Zachery Bir <a href="mailto:zbir@urbanape.com?subject=Zem%20Feedback">&lt;zbir@urbanape.com&gt;</a></p>

    <hr/>

    <p>&copy; 2003-2005, Zachery Bir and Zope Corporation. All rights
      reserved.</p>
  </body>
</html>
