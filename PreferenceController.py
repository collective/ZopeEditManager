#
#  PreferenceController.py
#  ZopeEditManager
#
#  Created by Zachery Bir on 2003-10-29.
#  Copyright (c) 2004 Zope Foundation and Contributors.
#

import os
import objc
from objc import YES, NO
from Foundation import *  # noqa
from AppKit import *  # noqa


def comparable_version(version_string):
    """
    Make comparable versions from strings, as received from os.uname()[2]
    """
    return [int(x) for x in version_string.split(".")]


MACOSX_VERSION = (
    comparable_version(os.uname()[2]) >= comparable_version("7.0.0")
    and "panther"
    or "jaguar"
)


def addToolbarItem(
    aController,
    anIdentifier,
    aLabel,
    aPaletteLabel,
    aToolTip,
    aTarget,
    anAction,
    anItemContent,
    aMenu,
):
    """
    Adds an freshly created item to the toolbar defined by
    aController.  Makes a number of assumptions about the
    implementation of aController.  It should be refactored into a
    generically useful toolbar management untility.
    """
    toolbarItem = NSToolbarItem.alloc().initWithItemIdentifier_(anIdentifier)

    toolbarItem.setLabel_(aLabel)
    toolbarItem.setPaletteLabel_(aPaletteLabel)
    toolbarItem.setToolTip_(aToolTip)
    toolbarItem.setTarget_(aTarget)
    if anAction:
        toolbarItem.setAction_(anAction)

    if type(anItemContent) == NSImage:
        toolbarItem.setImage_(anItemContent)
    else:
        toolbarItem.setView_(anItemContent)
        bounds = anItemContent.bounds()
        minSize = (100, bounds[1][1])
        maxSize = (1000, bounds[1][1])
        toolbarItem.setMinSize_(minSize)
        toolbarItem.setMaxSize_(maxSize)

    if aMenu:
        menuItem = NSMenuItem.alloc().init()
        menuItem.setSubmenu_(aMenu)
        menuItem.setTitle_(aMenu.title())
        toolbarItem.setMenuFormRepresentation_(menuItem)

    aController._toolbarItems[anIdentifier] = toolbarItem


class PreferenceController(NSWindowController):
    """
    The Controller object for managing various preference variables.
    """

    add_helper = objc.IBOutlet()
    always_borrow_webdav_locks = objc.IBOutlet()
    cleanup_files = objc.IBOutlet()
    confirm_on_finish = objc.IBOutlet()
    files_pane = objc.IBOutlet()
    helper_apps = objc.IBOutlet()
    helper_apps_pane = objc.IBOutlet()
    remove_helper = objc.IBOutlet()
    save_interval = objc.IBOutlet()
    temp_dir = objc.IBOutlet()
    use_webdav_locks = objc.IBOutlet()
    webdav_pane = objc.IBOutlet()

    @objc.IBAction
    def addHelper_(self, sender):
        lastIndex = self.numberOfRowsInTableView_(self.helper_apps)
        self._edited_fields.append(
            {
                "type": "Type %d" % lastIndex,
                "extension": "Ext %d" % lastIndex,
                "editor": "Editor %d" % lastIndex,
            }
        )
        self.helper_apps.reloadData()

    @objc.IBAction
    def removeHelper_(self, sender):
        row = self.helper_apps.selectedRow()
        if row != -1:
            del self._edited_fields[row]
            self.helper_apps.reloadData()

    @objc.IBAction
    def savePreferences_(self, sender):
        self.sud.setBool_forKey_(bool(self._cleanup_files), "cleanup_files")
        self.sud.setBool_forKey_(bool(self._confirm_on_finish), "confirm_on_finish")
        self.sud.setBool_forKey_(bool(self._use_webdav_locks), "use_locks")
        self.sud.setBool_forKey_(
            bool(self._always_borrow_webdav_locks), "always_borrow_locks"
        )
        self.sud.setFloat_forKey_(self._save_interval, "save_interval")
        self.sud.setObject_forKey_(self._temp_dir, "temp_dir")

        for field in self._edited_fields:
            self._helper_apps[field["type"]] = {
                "editor": field["editor"],
                "extension": field["extension"],
            }
        self.sud.setObject_forKey_(self._helper_apps, "helper_apps")

        self.sud.synchronize()

    @objc.IBAction
    def chooseTempDir_(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseDirectories_(True)
        panel.setCanChooseFiles_(False)
        panel.setAllowsMultipleSelection_(False)
        panel.setResolvesAliases_(True)
        bSFD = (
            panel.beginSheetForDirectory_file_types_modalForWindow_modalDelegate_didEndSelector_contextInfo_
        )
        bSFD(
            self._temp_dir,  # directory
            None,  # file
            None,  # types
            self.window(),  # modalForWindow
            self,  # modalDelegate
            self.chooseTempDirDidEnd_returnCode_contextInfo_,  # didEndSelector
            0,  # contextInfo
        )

    def chooseTempDirDidEnd_returnCode_contextInfo_(
        self, sheet, returnCode, contextInfo
    ):
        if returnCode:
            self._temp_dir = sheet.filenames()[0]
            self.temp_dir.setStringValue_(self._temp_dir)

    chooseTempDirDidEnd_returnCode_contextInfo_ = objc.selector(
        chooseTempDirDidEnd_returnCode_contextInfo_,
        selector=b"chooseTempDirDidEnd:returnCode:contextInfo:",
        signature=b"@@:@i@",
    )

    @objc.IBAction
    def setCleanupFiles_(self, sender):
        self._cleanup_files = self.cleanup_files.state()

    @objc.IBAction
    def setConfirmOnFinish_(self, sender):
        self._confirm_on_finish = self.confirm_on_finish.state()

    @objc.IBAction
    def setSaveInterval_(self, sender):
        self._save_interval = self.save_interval.floatValue()

    @objc.IBAction
    def setUseWebDAVLocks_(self, sender):
        self._use_webdav_locks = self.use_webdav_locks.state()
        if self._use_webdav_locks:
            self.always_borrow_webdav_locks.setEnabled_(YES)
        else:
            self.always_borrow_webdav_locks.setState_(0)
            self.always_borrow_webdav_locks.setEnabled_(NO)

    @objc.IBAction
    def setAlwaysBorrowWebDAVLocks_(self, sender):
        self._always_borrow_webdav_locks = self.always_borrow_webdav_locks.state()

    def windowWillClose_(self, sender):
        self.savePreferences_(self)

    def numberOfRowsInTableView_(self, tableView):
        return len(self._edited_fields)

    def tableView_objectValueForTableColumn_row_(self, tableView, aColumn, aRow):
        ident = aColumn.identifier()
        return self._edited_fields[aRow].get(ident, "")

    def tableView_setObjectValue_forTableColumn_row_(
        self, aTableView, anObject, aTableColumn, rowIndex
    ):
        ident = aTableColumn.identifier()
        self._edited_fields[rowIndex][ident] = anObject

    def tableView_shouldEditTableColumn_row_(self, aTableView, aTableColumn, rowIndex):
        return YES

    if MACOSX_VERSION == "panther":

        def tableView_sortDescriptorsDidChange_(self, aTableView, oldDescriptors):

            array = NSArray.arrayWithArray_(self._edited_fields)
            self._edited_fields = array.sortedArrayUsingDescriptors_(
                aTableView.sortDescriptors()
            )
            self.helper_apps.reloadData()

    def tableViewSelectionDidChange_(self, aNotification):
        if self.helper_apps.selectedRow() == -1:
            self.remove_helper.setEnabled_(NO)
            self.remove_helper.setImage_(self.remove_disabled)
        else:
            self.remove_helper.setEnabled_(YES)
            self.remove_helper.setImage_(self.remove_idle)

    def awakeFromNib(self):
        self.createToolbar()
        self.cleanup_files.setState_(self._cleanup_files and 1 or 0)
        self.confirm_on_finish.setState_(self._confirm_on_finish and 1 or 0)
        self.save_interval.setFloatValue_(
            self._save_interval and self._save_interval or 0.0
        )
        self.use_webdav_locks.setState_(self._use_webdav_locks and 1 or 0)
        self.always_borrow_webdav_locks.setState_(
            self._always_borrow_webdav_locks and 1 or 0
        )
        self.always_borrow_webdav_locks.setEnabled_(self._use_webdav_locks and 1 or 0)
        self.temp_dir.setStringValue_(self._temp_dir)

        if MACOSX_VERSION == "panther":
            self.helper_apps.tableColumnWithIdentifier_(
                "type"
            ).setSortDescriptorPrototype_(self.typeDescriptor)
            self.helper_apps.tableColumnWithIdentifier_(
                "editor"
            ).setSortDescriptorPrototype_(self.editorDescriptor)
            self.helper_apps.tableColumnWithIdentifier_(
                "extension"
            ).setSortDescriptorPrototype_(self.extensionDescriptor)
            self.helper_apps.setSortDescriptors_(
                [
                    self.typeDescriptor,
                ]
            )

        self.cached_window_frame = self.window().frame()
        self.cached_files_pane_frame = self.files_pane.frame()
        self.cached_webdav_pane_frame = self.webdav_pane.frame()
        self.cached_helper_apps_pane_frame = self.helper_apps_pane.frame()

        self.remove_helper.setEnabled_(NO)
        self.remove_helper.setImage_(self.remove_disabled)

        self.window().toolbar().setSelectedItemIdentifier_("Files Pane")
        self.showFilesPane_(self)

    def createToolbar(self):
        toolbar = NSToolbar.alloc().initWithIdentifier_("Preferences Window")
        toolbar.setDelegate_(self)
        toolbar.setAllowsUserCustomization_(NO)
        toolbar.setAutosavesConfiguration_(YES)

        self.createToolbarItems()

        self.window().setToolbar_(toolbar)

    def createToolbarItems(self):
        addToolbarItem(
            self,
            "Files Pane",
            "Files",
            "Files",
            "Set File Preferences",
            None,
            "showFilesPane:",
            NSImage.imageNamed_("Files"),
            None,
        )

        addToolbarItem(
            self,
            "WebDAV Pane",
            "WebDAV",
            "WebDAV",
            "Set WebDAV Preferences",
            None,
            "showWebDAVPane:",
            NSImage.imageNamed_("WebDAV"),
            None,
        )

        addToolbarItem(
            self,
            "Helper Apps Pane",
            "Helper Apps",
            "Helper Apps",
            "Set Helper Apps Preferences",
            None,
            "showHelperAppsPane:",
            NSImage.imageNamed_("HelperApps"),
            None,
        )

        self._toolbarDefaultItemIdentifiers = [
            "Files Pane",
            "WebDAV Pane",
            "Helper Apps Pane",
        ]

    def toolbarDefaultItemIdentifiers_(self, anIdentifier):
        return self._toolbarDefaultItemIdentifiers

    def toolbarAllowedItemIdentifiers_(self, anIdentifier):
        return self._toolbarDefaultItemIdentifiers

    def toolbarSelectableItemIdentifiers_(self, anIdentifier):
        return self._toolbarDefaultItemIdentifiers

    def toolbarWillAddItem_(self, notification):
        pass

    def toolbarDidRemoveItem_(self, notification):
        pass

    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(
        self, toolbar, itemIdentifier, flag
    ):
        newItem = NSToolbarItem.alloc().initWithItemIdentifier_(itemIdentifier)
        item = self._toolbarItems[itemIdentifier]

        newItem.setLabel_(item.label())
        newItem.setPaletteLabel_(item.paletteLabel())
        if item.view():
            newItem.setView_(item.view())
        else:
            newItem.setImage_(item.image())

        newItem.setToolTip_(item.toolTip())
        newItem.setTarget_(item.target())
        newItem.setAction_(item.action())
        newItem.setMenuFormRepresentation_(item.menuFormRepresentation())

        if newItem.view():
            newItem.setMinSize_(item.minSize())
            newItem.setMaxSize_(item.maxSize())

        return newItem

    def showFilesPane_(self, sender):
        self.resizeViewFor_(self.cached_files_pane_frame)
        self.window().setContentView_(self.files_pane)

    def showWebDAVPane_(self, sender):
        self.resizeViewFor_(self.cached_webdav_pane_frame)
        self.window().setContentView_(self.webdav_pane)

    def showHelperAppsPane_(self, sender):
        self.resizeViewFor_(self.cached_helper_apps_pane_frame)
        self.window().setContentView_(self.helper_apps_pane)

    def resizeViewFor_(self, view_frame):
        windowFrame = self.window().contentRectForFrameRect_styleMask_(
            self.window().frame(), self.window().styleMask()
        )
        newWindowHeight = NSHeight(view_frame)
        toolbarHeight = 0.0
        if self.window().toolbar().isVisible():
            toolbarHeight = NSHeight(self.window().toolbar()._toolbarView().frame())
        newWindowFrame = self.window().frameRectForContentRect_styleMask_(
            (
                (NSMinX(windowFrame), NSMaxY(windowFrame) - newWindowHeight),
                (NSWidth(windowFrame), newWindowHeight),
            ),
            self.window().styleMask(),
        )
        self.window().setFrame_display_animate_(
            newWindowFrame, YES, self.window().isVisible()
        )

    def init(self):
        self = self.initWithWindowNibName_("Preferences")

        self._edited_fields = []
        self._toolbarItems = {}
        self._toolbarDefaultItemIdentifiers = []

        self.sud = NSUserDefaults.standardUserDefaults()
        self._cleanup_files = self.sud.boolForKey_("cleanup_files")
        self._confirm_on_finish = self.sud.boolForKey_("confirm_on_finish")
        self._save_interval = self.sud.floatForKey_("save_interval")
        self._use_webdav_locks = self.sud.boolForKey_("use_locks")
        self._always_borrow_webdav_locks = self.sud.boolForKey_("always_borrow_locks")
        self._helper_apps = NSMutableDictionary.dictionaryWithDictionary_(
            self.sud.dictionaryForKey_("helper_apps")
        )
        self._temp_dir = self.sud.stringForKey_("temp_dir") or "/tmp"

        # This button will change, so we should pre-load them
        self.remove_idle = NSImage.imageNamed_("remove_idle")
        self.remove_disabled = NSImage.imageNamed_("remove_disabled")

        for x in range(len(self._helper_apps.keys())):
            type = [e for e in self._helper_apps.keys()][x]
            extension = self._helper_apps[type].get("extension", "")
            editor = self._helper_apps[type].get("editor", "")
            self._edited_fields.append(
                {"type": type, "extension": extension, "editor": editor}
            )

        if MACOSX_VERSION == "panther":
            self.typeDescriptor = (
                NSSortDescriptor.alloc().initWithKey_ascending_selector_(
                    "type", YES, "caseInsensitiveCompare:"
                )
            )

            self.editorDescriptor = (
                NSSortDescriptor.alloc().initWithKey_ascending_selector_(
                    "editor", YES, "caseInsensitiveCompare:"
                )
            )

            self.extensionDescriptor = (
                NSSortDescriptor.alloc().initWithKey_ascending_selector_(
                    "extension", YES, "caseInsensitiveCompare:"
                )
            )

        return self
