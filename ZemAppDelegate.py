#
#  ZemAppDelegate.py
#  Zem
#
#  Created by Zachery Bir on Thu Jun 10 2004.
#  Copyright (c) 2004 Zope Foundation and Contributors.
#

# library imports
import os, re
from objc import YES, NO
from PyObjCTools import AppHelper

# import needed classes/functions from Foundation
from Foundation import *

# import Nib loading functionality from AppKit
from AppKit import *

# local product imports
from ZopeDocument import ZopeDocument, __version__
from PreferenceController import PreferenceController

def iterNSIndexSet(s):
    val = s.lastIndex()
    while val != NSNotFound:
        yield val
        val = s.indexLessThanIndex_(val)

class ZemAppDelegate(NSObject):
    """
    The Controller object for managing various processes editing Zope
    objects externally.
    """

    current_edits = objc.IBOutlet()
    finish = objc.IBOutlet()
    sync_message = objc.IBOutlet()
    sync_spinner = objc.IBOutlet()
    window = objc.IBOutlet()

    def updateIfModified(self, timer):
        timerUser = timer.userInfo()
        for doc in timerUser.current_edits_data:
            mtime = os.path.getmtime(doc.getContentFile())

            if mtime != doc.last_mtime:
                # File was modified
                self.sync_spinner.startAnimation_(self)
                doc.putChanges()
                self.sync_spinner.stopAnimation_(self)
                self.sync_message.setStringValue_(u'Last synched: %s' % NSDate.date().descriptionWithCalendarFormat_timeZone_locale_(u"%a, %d %b %Y at %H:%M:%S %p", None, None))
                doc.last_mtime = mtime

        return 1

    @objc.IBAction
    def performClose_(self, sender):
        keyWindow = NSApplication.sharedApplication().keyWindow()
        if keyWindow is self.window:
            return NO
        keyWindow.performClose_(sender)

    @objc.IBAction
    def showPreferencePanel_(self, sender):
        if self.preferenceController is None:
            self.preferenceController = PreferenceController.alloc().init()
        self.preferenceController.showWindow_(self)

    def application_openFile_(self, app, filename):
        """
        Invoked by NSApplication when the app attempts to open a file
        """
        NSLog(u'Opening Application')

        zopeDoc = ZopeDocument(filename)
        zopeDoc.removeFileIfNecessary(filename)
        self.current_edits_data.append(zopeDoc)
        self.current_edits.reloadData()
        return self.openDocument_(zopeDoc)

    @objc.IBAction
    def gotoEdit_(self, sender):
        row = self.current_edits.selectedRow()
        if row != -1:
            zopeDoc = self.current_edits_data[row]
            return self.openDocument_(zopeDoc)

    @objc.IBAction
    def openDocument_(self, zopeDoc):
        if self.sud.boolForKey_(u'use_locks'):
            if zopeDoc.metadata.get(u'lock-token'):
                if (self.sud.boolForKey_(u'always_borrow_locks')
                    or zopeDoc.metadata.get(u'borrow_lock')
                    or NSRunAlertPanel(u"Borrow Lock?",
                                       u"This object is already locked by"
                                       " you in another session. Do you want"
                                       " to borrow this lock and continue?",
                                       u"Yes", u"Cancel", None)):
                    zopeDoc.lock_token = (u'opaquelocktoken:%s'
                                          % zopeDoc.metadata['lock-token'])
            else:
                self.finishEdits_()

        if self.sud.boolForKey_(u'use_locks'):
            zopeDoc.lock()

        editor = zopeDoc.getEditor()
        content_file = zopeDoc.getContentFile()
        return self.ws.openFile_withApplication_andDeactivate_(content_file,
                                                               editor, YES)

    @objc.IBAction
    def finishEdits_(self, sender=None):
        """
        We want to get rid of the lock on one or more Zope objects and
        delete its local copy.
        """
        selected = self.current_edits.numberOfSelectedRows()
        if selected:
            perform = True
            if self.sud.boolForKey_(u'confirm_on_finish'):
                if selected == 1:
                    msg = u"Are you sure you're finished with this object?"
                else:
                    msg = (u"Are you sure you're finished with these %d "
                           "objects?" % (selected))
                perform = NSRunAlertPanel(u"Deleting Entry", msg,
                                          u"Yes", u"Cancel", None)
            for row in iterNSIndexSet(self.current_edits.selectedRowIndexes()):
                del self.current_edits_data[row]
                self.current_edits.reloadData()

    def numberOfRowsInTableView_(self, tableView):
        return len(self.current_edits_data)

    def tableView_objectValueForTableColumn_row_(self, tableView,
                                                 aColumn, aRow):
        ident = aColumn.identifier()
        return getattr(self.current_edits_data[aRow], 'get' + ident)()

    def tableViewSelectionDidChange_(self, aNotification):
        if self.current_edits.selectedRow() == -1:
            self.finish.setEnabled_(NO)
        else:
            self.finish.setEnabled_(YES)

    def upgradePrefs(self):
        new_prefs = {}
        keep_keys = [u'always_borrow_locks', u'cleanup_files',
                     u'confirm_on_finish', u'helper_apps', u'save_interval',
                     u'use_locks', u'version_check']
        for key in keep_keys:
            new_prefs[key] = self.sud.objectForKey_(key)
        edit_keys = self.sud.persistentDomainForName_(self.bundleIdent).keys()
        helper_apps = self.sud.dictionaryForKey_(u'helper_apps')
        if helper_apps is None:
            helper_apps = {}
        for key in edit_keys:
            if key not in keep_keys:
                if self.sud.objectForKey_(key).has_key(u'editor'):
                    helper_apps[key] = self.sud.objectForKey_(key)
                else:
                    sub_keys = self.sud.objectForKey_(key).keys()
                    for sub_key in sub_keys:
                        helper_apps[u"%s/%s" % (key, sub_key)] = self.sud.objectForKey_(key)[sub_key]
        new_prefs[u'helper_apps'] = helper_apps

        # Possibly a new pref this version
        if not new_prefs.has_key(u'confirm_on_finish'):
            new_prefs[u'confirm_on_finish'] = YES

        # Update this pref always
        new_prefs[u'version_check'] = __version__

        self.sud.removePersistentDomainForName_(self.bundleIdent)
        self.sud.setPersistentDomain_forName_(new_prefs, self.bundleIdent)
        self.sud.synchronize()
        NSRunAlertPanel(u"Preferences Updated",
                        u"Your Preferences have been upgraded.",
                        u"Close", None, None)

    def resetPrefs(self):
        self.sud.removePersistentDomainForName_(self.bundleIdent)
        self.sud.setPersistentDomain_forName_(
            NSDictionary.dictionaryWithContentsOfFile_(
                NSBundle.mainBundle().pathForResource_ofType_(
                    self.bundleIdent, "plist")),
            self.bundleIdent)
        self.sud.synchronize()
        if NSRunAlertPanel(u"Preferences Reset",
                           u"Your Preferences have been reset.",
                           u"Edit Prefs", u"Close", None):
            self.showPreferencePanel_(self)

    def awakeFromNib(self):
        self.current_edits.setDoubleAction_("gotoEdit:")
        self.sync_message.setStringValue_(u'')
        self.finish.setEnabled_(NO)

    def init(self):
        self.bundleIdent = NSBundle.mainBundle().bundleIdentifier()
        self.preferenceController = None
        self.current_edits_data = []
        self.ws = NSWorkspace.sharedWorkspace()
        NSUserDefaults.resetStandardUserDefaults()
        self.sud = NSUserDefaults.standardUserDefaults()
        pdomain = self.sud.persistentDomainForName_(self.bundleIdent)
        if pdomain is None:
            self.sud.setPersistentDomain_forName_(
                NSDictionary.dictionaryWithContentsOfFile_(
                    NSBundle.mainBundle().pathForResource_ofType_(
                        self.bundleIdent, "plist")),
                self.bundleIdent)
            self.sud.synchronize()

        version_check = self.sud.stringForKey_(u'version_check')
        if version_check != __version__:
            response =  NSRunAlertPanel(u"Preferences Differ",
                                        u"Your Preferences were set with "
                                        "an older version of "
                                        "Zem. Would you "
                                        "like to upgrade your Preferences?",
                                        u"Upgrade", u"Start Fresh", None)
            if response == 1:
                self.upgradePrefs()
            if response == 0:
                self.resetPrefs()

        interval = (self.sud.floatForKey_(u'save_interval')) or 20.0
        timer = (
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                interval, self, 'updateIfModified', self, YES))
        NSRunLoop.currentRunLoop().addTimer_forMode_(timer,
                                                     NSDefaultRunLoopMode)

        return self

    def applicationWillTerminate_(self, notification):
        for x in range(len(self.current_edits_data)):
            del self.current_edits_data[x]

AppHelper.runEventLoop(argv=[])
