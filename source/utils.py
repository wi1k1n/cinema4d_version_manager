import sys, os, re, uuid, json, psutil, signal, ctypes
import datetime as dt
import win32process, win32gui, win32con, win32api, win32com.client
from typing import Any, Callable, TypeVar
import keyboard

from PyQt5.QtCore import QUrl, QMimeData, QProcess
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication

RES_FOLDER = os.path.join(os.getcwd(), 'res')
IMAGES_FOLDER = os.path.join(RES_FOLDER, 'images')
C4D_ICONS_FOLDER = os.path.join(IMAGES_FOLDER, 'c4d')

C4DTAG_MIMETYPE = 'text/c4dtaguuid'

APPLICATION_FONT_FAMILY = 'SblHebrew'

def GenerateUUID() -> str:
	return str(uuid.uuid4())

def GetPrefsFolderPath() -> str:
	path: str = os.path.join(GetAppDataPath(), 'c4d-version-manager')
	os.makedirs(path, exist_ok=True)
	return path

def GetAppDataPath() -> str:
	return os.getenv('APPDATA')

def GetStartupPath() -> str | None:
	# https://stackoverflow.com/questions/23500274/what-exactly-does-win32com-client-dispatchwscript-shell
	# https://stackoverflow.com/questions/27127710/find-startup-folder-in-windows-8-using-python/27130194#27130194
	try:
		objShell = win32com.client.Dispatch('WScript.Shell')
		return objShell.SpecialFolders('Startup')
	except Exception as e:
		print(e)
		return None

def CreateSymlink(src: str, dst: str) -> bool:
	if not os.path.isfile(src) or os.path.exists(dst):
		return False
	os.symlink(src, dst)
	return True

def GetCurrentExecutablePath() -> str:
	appDir: str = ''
	# https://stackoverflow.com/a/42615559/5765191
	if getattr(sys, 'frozen', False):
		# If the application is run as a bundle, the PyInstaller bootloader
		# extends the sys module by a flag frozen=True and sets the app 
		# path into variable _MEIPASS'.
		appDir = sys._MEIPASS
	else:
		appDir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(appDir, os.path.split(sys.argv[0])[1])

def CopyFileToClipboard(src: str) -> bool:
	if not os.path.isfile(src):
		return False
	data: QMimeData = QMimeData()
	data.setUrls([QUrl.fromLocalFile(src)])
	QApplication.clipboard().setMimeData(data)
	return True

def ShowFileInDefaultExplorer(path: str) -> None:
	# https://stackoverflow.com/a/42815083/5765191
	if not os.path.isfile(path):
		return
	QProcess().startDetached('explorer /e, /select, "' + os.path.abspath(path) + '"')

def OpenFolderInDefaultExplorer(path: str) -> None:
	if os.path.isdir(path):
		QDesktopServices.openUrl(QUrl.fromLocalFile(path))

def OpenURL(url: str) -> None:
	QDesktopServices.openUrl(QUrl(url))

def GetFolderTimestampCreated(path: str) -> dt.datetime:
	if os.path.exists(path):
		return dt.datetime.fromtimestamp(os.stat(path).st_ctime)
	return dt.datetime.now()

class WinUtils:
	EnumWindows = ctypes.windll.user32.EnumWindows
	EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
	GetWindowText = ctypes.windll.user32.GetWindowTextW
	GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
	IsWindowVisible = ctypes.windll.user32.IsWindowVisible

	@staticmethod
	def IsPIDExisting(pid: int) -> bool:
		return psutil.pid_exists(pid)

	@staticmethod
	def KillProcessByPID(pid: int):
		if WinUtils.IsPIDExisting(pid):
			os.kill(pid, signal.SIGTERM)

	@staticmethod
	def getWindowTitleByHandle(hwnd):
		length = WinUtils.GetWindowTextLength(hwnd)
		buff = ctypes.create_unicode_buffer(length + 1)
		WinUtils.GetWindowText(hwnd, buff, length + 1)
		return buff.value

	@staticmethod # https://stackoverflow.com/a/70659506/5765191
	def getHWNDsForPID(pid):
		def callback(hwnd, hwnds):
			#if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
			_, foundPID = win32process.GetWindowThreadProcessId(hwnd)
			if foundPID == pid:
				hwnds.append(hwnd)
			return True
		hwnds = []
		win32gui.EnumWindows(callback, hwnds)
		return hwnds
	
	@staticmethod
	def getProcessIDByName():
		qobuz_pids = []
		process_name = "Qobuz.exe"
		for proc in psutil.process_iter():
			if process_name in proc.name():
				qobuz_pids.append(proc.pid)
		return qobuz_pids
	
	@staticmethod # https://stackoverflow.com/a/2091530/5765191
	def setWindowForeground(hwnd: int):
		win32gui.SetForegroundWindow(hwnd)
	
	@staticmethod # https://stackoverflow.com/a/60471554/5765191
	def getWindowPlacement(hwnd: int) -> int:
		tup = win32gui.GetWindowPlacement(hwnd)
		if tup[1] == win32con.SW_SHOWMAXIMIZED:
			return 1
		if tup[1] == win32con.SW_SHOWMINIMIZED:
			return -1
		return 0

	@staticmethod
	def isWindowMinimized(hwnd: int):
		return WinUtils.getWindowPlacement(hwnd) == -1
	@staticmethod
	def isWindowMaximized(hwnd: int):
		return WinUtils.getWindowPlacement(hwnd) == 1

	@staticmethod # https://stackoverflow.com/a/2791681/5765191
	def maximizeWindow(hwnd: int):
		win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

class KeyboardManager:
	@staticmethod
	def RegisterHotkey(hotkey: str, cb, args: list[Any]):
		keyboard.add_hotkey(hotkey, cb, args)
	@staticmethod
	def UnregisterHotkey(hotkeyOrCb: str) -> bool:
		keyboard.remove_hotkey(hotkeyOrCb)

# Tries to cast given value to type, falls back to default if error
def SafeCast(val, to_type, default=None):
	try:
		return to_type(val)
	except (ValueError, TypeError):
		return default

# Extra information binded to the existing c4d package
class C4DCacheInfo:
	def __init__(self, tagUuids: list[str] = [], note: str = '') -> None:
		self.tagUuids: list[str] = tagUuids
		self.note: str = note
		
		# Session related, is not stored
		self.processStatus: int = 0 # 0 - not started yet; -1 started and closed; -2 - started and killed, > 0 - running
	
	def ToJSON(self) -> dict:
		return {
			'tagUuids': self.tagUuids,
			'note': self.note,
		}
	
	@staticmethod
	def FromJSON(jsonStr: str):
		tagUuids: list[str] = jsonStr['tagUuids'] if 'tagUuids' in jsonStr else ''
		note: str = jsonStr['note'] if 'note' in jsonStr else ''
		return C4DCacheInfo(tagUuids, note)

# Information about cinema that can be extracted from filesystem
class C4DInfo:
	def __init__(self, dir: str, ver: list[str], dirPrefs: str | None = None) -> None:
		self.version: list[str] = ver
		self.directory: str = dir
		self.directoryPrefs: str = dirPrefs if dirPrefs else ''

	def GetPathExecutable(self) -> str:
		return os.path.join(self.directory, 'Cinema 4D.exe')

	def GetPathConfigCinema(self) -> str:
		return os.path.join(self.GetPathFolderResource(), 'config.cinema4d.txt')
	
	def GetPathFolderRoot(self) -> str:
		return self.directory
	
	def GetNameFolderRoot(self) -> str:
		return os.path.basename(self.GetPathFolderRoot())

	def GetPathFolderResource(self) -> str:
		return os.path.join(self.directory, 'resource')
	
	def GetPathFolderPrefs(self) -> str:
		return self.directoryPrefs

	def GetPathFolderPlugins(self) -> str:
		return os.path.join(self.directoryPrefs, 'plugins')
	
	def GetVersionString(self, formatted: bool = True, full: bool = False) -> str:
		major: str = self.version[0]
		if len(major) == 4: # new convention
			return '.'.join(self.version if full else self.version[:-1])
		return self.GetVersionMajor(formatted) + '.' + ''.join(self.version[1:])

	def GetVersionMajor(self, formatted: bool = True) -> str:
		major: str = self.version[0]
		return ('R' if len(major) != 4 and formatted else '') + major

class C4DTileGroup:
	def __init__(self, indices: list[int] = list(), name: str = '', key: Any = None) -> None:
		self.indices = indices
		self.name = name
		self.key: Any = key
	
	def __eq__(self, other) -> bool:
		if isinstance(other, C4DTileGroup):
			return self.key == other.key
		raise NotImplemented('C4DTileGroup: cannot compare')
	
	def __hash__(self) -> int:
		return hash(self.key)

# Tries to find corresponding preferences folder in the APPDATA directory
def FindC4DPrefsFolder(folderPath: str) -> str | None:
	appDataMaxonPath: str = os.path.join(GetAppDataPath(), 'Maxon')
	if not os.path.isdir(appDataMaxonPath):
		return None
	
	c4dDirName: str = os.path.basename(folderPath)
	c4dDirNameLen: int = len(c4dDirName)
	suffixPattern: str = '^_[A-Z0-9]{8}'

	dirNames: list[str] = [f.name for f in os.scandir(appDataMaxonPath) if f.is_dir()]
	for dir in dirNames:
		if not dir.startswith(c4dDirName):
			continue
		suffix: str = dir[c4dDirNameLen:]
		if not re.match(suffixPattern, suffix):
			continue
		return os.path.join(appDataMaxonPath, dir)
	return None

# Checks given folder path for containing Cinema 4D version
C4D_NECESSARY_FILES = ['Cinema 4D.exe']
C4D_NECESSARY_FOLDERS = ['corelibs', 'resource']
def GetC4DInfoFromFolder(folderPath: str) -> C4DInfo | None:
	for file in C4D_NECESSARY_FILES:
		curPath: str = os.path.join(folderPath, file)
		if not os.path.isfile(curPath):
			return None
	for file in C4D_NECESSARY_FOLDERS:
		curPath: str = os.path.join(folderPath, file)
		if not os.path.isdir(curPath):
			return None

	# Get Cinema version
	versionPath: str = os.path.join(folderPath, 'resource', 'version.h')
	if not os.path.isfile(versionPath):
		return None

	C4V_VERSION_PART_PREFIX: str = '#define C4D_V'
	c4dVersion: dict = {1: -1, 2: -1, 3: -1, 4: -1}
	versionPartCnt: int = 0
	with open(versionPath) as fp:
		while versionPartCnt < 4:
			line: str = fp.readline().strip()
			if line is None:
				break
			for i in range(1, 5):
				curDefinePart: str = C4V_VERSION_PART_PREFIX + str(i)
				if line.startswith(curDefinePart):
					c4dVersion[i] = SafeCast(line[len(curDefinePart):].strip(), int, -1)
					versionPartCnt += 1
					break
	# validate cinema version
	for v in c4dVersion.values():
		if v == -1:
			return None

	versionStringsList: list[str] = [str(v) for v in c4dVersion.values()]
	prefsFolder: str | None = FindC4DPrefsFolder(folderPath)
	return C4DInfo(folderPath, versionStringsList, prefsFolder)

# Traverses directory until maxDepth, returns dict: path -> c4d_version
def FindCinemaPackagesInFolder(path, maxDepth = 2) -> dict[str, C4DInfo]:
	c4dRootInfo: C4DInfo | None = GetC4DInfoFromFolder(path)
	if c4dRootInfo:
		return {path: c4dRootInfo}

	def getDirList(pathDir: str) -> list[str]:
		try:
			dirList: list[str] = [os.path.join(pathDir, d) for d in os.listdir(pathDir)]
			return list(filter(lambda d: os.path.isdir(d), dirList))
		except:
			pass
		return list()
	
	ret: dict[str, C4DInfo] = dict()
	dirs: set[str] = set(getDirList(path))
	currentDepth: int = 0
	while len(dirs) and currentDepth < maxDepth:
		newDirs: list[str] = []
		for p in dirs:
			c4dInfo: C4DInfo | None = GetC4DInfoFromFolder(p)
			if c4dInfo:
				ret[p] = c4dInfo
				continue
			newDirs += getDirList(p)
		dirs = newDirs
		currentDepth += 1
	return ret

qEventLookup = {"0": "QEvent::None",
				"114": "QEvent::ActionAdded",
				"113": "QEvent::ActionChanged",
				"115": "QEvent::ActionRemoved",
				"99": "QEvent::ActivationChange",
				"121": "QEvent::ApplicationActivate",
				"122": "QEvent::ApplicationDeactivate",
				"36": "QEvent::ApplicationFontChange",
				"37": "QEvent::ApplicationLayoutDirectionChange",
				"38": "QEvent::ApplicationPaletteChange",
				"214": "QEvent::ApplicationStateChange",
				"35": "QEvent::ApplicationWindowIconChange",
				"68": "QEvent::ChildAdded",
				"69": "QEvent::ChildPolished",
				"71": "QEvent::ChildRemoved",
				"40": "QEvent::Clipboard",
				"19": "QEvent::Close",
				"200": "QEvent::CloseSoftwareInputPanel",
				"178": "QEvent::ContentsRectChange",
				"82": "QEvent::ContextMenu",
				"183": "QEvent::CursorChange",
				"52": "QEvent::DeferredDelete",
				"60": "QEvent::DragEnter",
				"62": "QEvent::DragLeave",
				"61": "QEvent::DragMove",
				"63": "QEvent::Drop",
				"170": "QEvent::DynamicPropertyChange",
				"98": "QEvent::EnabledChange",
				"10": "QEvent::Enter",
				"150": "QEvent::EnterEditFocus",
				"124": "QEvent::EnterWhatsThisMode",
				"206": "QEvent::Expose",
				"116": "QEvent::FileOpen",
				"8": "QEvent::FocusIn",
				"9": "QEvent::FocusOut",
				"23": "QEvent::FocusAboutToChange",
				"97": "QEvent::FontChange",
				"198": "QEvent::Gesture",
				"202": "QEvent::GestureOverride",
				"188": "QEvent::GrabKeyboard",
				"186": "QEvent::GrabMouse",
				"159": "QEvent::GraphicsSceneContextMenu",
				"164": "QEvent::GraphicsSceneDragEnter",
				"166": "QEvent::GraphicsSceneDragLeave",
				"165": "QEvent::GraphicsSceneDragMove",
				"167": "QEvent::GraphicsSceneDrop",
				"163": "QEvent::GraphicsSceneHelp",
				"160": "QEvent::GraphicsSceneHoverEnter",
				"162": "QEvent::GraphicsSceneHoverLeave",
				"161": "QEvent::GraphicsSceneHoverMove",
				"158": "QEvent::GraphicsSceneMouseDoubleClick",
				"155": "QEvent::GraphicsSceneMouseMove",
				"156": "QEvent::GraphicsSceneMousePress",
				"157": "QEvent::GraphicsSceneMouseRelease",
				"182": "QEvent::GraphicsSceneMove",
				"181": "QEvent::GraphicsSceneResize",
				"168": "QEvent::GraphicsSceneWheel",
				"18": "QEvent::Hide",
				"27": "QEvent::HideToParent",
				"127": "QEvent::HoverEnter",
				"128": "QEvent::HoverLeave",
				"129": "QEvent::HoverMove",
				"96": "QEvent::IconDrag",
				"101": "QEvent::IconTextChange",
				"83": "QEvent::InputMethod",
				"207": "QEvent::InputMethodQuery",
				"169": "QEvent::KeyboardLayoutChange",
				"6": "QEvent::KeyPress",
				"7": "QEvent::KeyRelease",
				"89": "QEvent::LanguageChange",
				"90": "QEvent::LayoutDirectionChange",
				"76": "QEvent::LayoutRequest",
				"11": "QEvent::Leave",
				"151": "QEvent::LeaveEditFocus",
				"125": "QEvent::LeaveWhatsThisMode",
				"88": "QEvent::LocaleChange",
				"176": "QEvent::NonClientAreaMouseButtonDblClick",
				"174": "QEvent::NonClientAreaMouseButtonPress",
				"175": "QEvent::NonClientAreaMouseButtonRelease",
				"173": "QEvent::NonClientAreaMouseMove",
				"177": "QEvent::MacSizeChange",
				"43": "QEvent::MetaCall",
				"102": "QEvent::ModifiedChange",
				"4": "QEvent::MouseButtonDblClick",
				"2": "QEvent::MouseButtonPress",
				"3": "QEvent::MouseButtonRelease",
				"5": "QEvent::MouseMove",
				"109": "QEvent::MouseTrackingChange",
				"13": "QEvent::Move",
				"197": "QEvent::NativeGesture",
				"208": "QEvent::OrientationChange",
				"12": "QEvent::Paint",
				"39": "QEvent::PaletteChange",
				"131": "QEvent::ParentAboutToChange",
				"21": "QEvent::ParentChange",
				"212": "QEvent::PlatformPanel",
				"217": "QEvent::PlatformSurface",
				"75": "QEvent::Polish",
				"74": "QEvent::PolishRequest",
				"123": "QEvent::QueryWhatsThis",
				"106": "QEvent::ReadOnlyChange",
				"199": "QEvent::RequestSoftwareInputPanel",
				"14": "QEvent::Resize",
				"204": "QEvent::ScrollPrepare",
				"205": "QEvent::Scroll",
				"117": "QEvent::Shortcut",
				"51": "QEvent::ShortcutOverride",
				"17": "QEvent::Show",
				"26": "QEvent::ShowToParent",
				"50": "QEvent::SockAct",
				"192": "QEvent::StateMachineSignal",
				"193": "QEvent::StateMachineWrapped",
				"112": "QEvent::StatusTip",
				"100": "QEvent::StyleChange",
				"87": "QEvent::TabletMove",
				"92": "QEvent::TabletPress",
				"93": "QEvent::TabletRelease",
				"171": "QEvent::TabletEnterProximity",
				"172": "QEvent::TabletLeaveProximity",
				"219": "QEvent::TabletTrackingChange",
				"22": "QEvent::ThreadChange",
				"1": "QEvent::Timer",
				"120": "QEvent::ToolBarChange",
				"110": "QEvent::ToolTip",
				"184": "QEvent::ToolTipChange",
				"194": "QEvent::TouchBegin",
				"209": "QEvent::TouchCancel",
				"196": "QEvent::TouchEnd",
				"195": "QEvent::TouchUpdate",
				"189": "QEvent::UngrabKeyboard",
				"187": "QEvent::UngrabMouse",
				"78": "QEvent::UpdateLater",
				"77": "QEvent::UpdateRequest",
				"111": "QEvent::WhatsThis",
				"118": "QEvent::WhatsThisClicked",
				"31": "QEvent::Wheel",
				"132": "QEvent::WinEventAct",
				"24": "QEvent::WindowActivate",
				"103": "QEvent::WindowBlocked",
				"25": "QEvent::WindowDeactivate",
				"34": "QEvent::WindowIconChange",
				"105": "QEvent::WindowStateChange",
				"33": "QEvent::WindowTitleChange",
				"104": "QEvent::WindowUnblocked",
				"203": "QEvent::WinIdChange",
				"126": "QEvent::ZOrderChange", }