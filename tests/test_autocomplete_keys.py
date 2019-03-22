from __future__ import absolute_import
import sys
import os


sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)

from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore, QtTest

ignored_keys = [
QtCore.Qt.Key_Excel,
QtCore.Qt.Key_DOS,
QtCore.Qt.Key_Dead_Belowdot,
QtCore.Qt.Key_LaunchH,
QtCore.Qt.Key_LaunchG,
QtCore.Qt.Key_Dead_Caron,
QtCore.Qt.Key_Hangul_Special,
QtCore.Qt.Key_Hangul_Jamo,
QtCore.Qt.Key_Dead_Voiced_Sound,
QtCore.Qt.Key_OfficeHome,
QtCore.Qt.Key_UWB,
QtCore.Qt.Key_Katakana,
QtCore.Qt.Key_Eisu_toggle,
QtCore.Qt.Key_Zoom,
QtCore.Qt.Key_Zenkaku,
QtCore.Qt.Key_Save,
QtCore.Qt.Key_WebCam,
QtCore.Qt.Key_MenuKB,
QtCore.Qt.Key_Video,
QtCore.Qt.Key_Multi_key,
QtCore.Qt.Key_Dead_Horn,
QtCore.Qt.Key_Hangul_Hanja,
QtCore.Qt.Key_Call,
QtCore.Qt.Key_AudioForward,
QtCore.Qt.Key_Ccedilla,
QtCore.Qt.Key_Away,
QtCore.Qt.Key_MenuPB,
QtCore.Qt.Key_Hangul_Jeonja,
QtCore.Qt.Key_Hankaku,
QtCore.Qt.Key_Dead_Semivoiced_Sound,
QtCore.Qt.Key_Dead_Tilde,
QtCore.Qt.Key_ScreenSaver,
QtCore.Qt.Key_Game,
QtCore.Qt.Key_AudioRewind,
QtCore.Qt.Key_Hangul_Banja,
QtCore.Qt.Key_Ugrave,
QtCore.Qt.Key_Printer,
QtCore.Qt.Key_Xfer,
QtCore.Qt.Key_AltGr,
QtCore.Qt.Key_Kana_Lock,
QtCore.Qt.Key_Subtitle,
QtCore.Qt.Key_KeyboardBrightnessUp,
QtCore.Qt.Key_Market,
QtCore.Qt.Key_MediaPause,
QtCore.Qt.Key_Suspend,
QtCore.Qt.Key_Send,
QtCore.Qt.Key_Travel,
QtCore.Qt.Key_ApplicationLeft,
QtCore.Qt.Key_Hiragana,
QtCore.Qt.Key_TaskPane,
QtCore.Qt.Key_MediaTogglePlayPause,
QtCore.Qt.Key_LastNumberRedial,
QtCore.Qt.Key_Muhenkan,
QtCore.Qt.Key_Option,
QtCore.Qt.Key_Phone,
QtCore.Qt.Key_MailForward,
QtCore.Qt.Key_ApplicationRight,
QtCore.Qt.Key_Community,
QtCore.Qt.Key_LightBulb,
QtCore.Qt.Key_Hangul_PreHanja,
QtCore.Qt.Key_Hangul_Romaja,
QtCore.Qt.Key_Calculator,
QtCore.Qt.Key_ClearGrab,
QtCore.Qt.Key_AE,
QtCore.Qt.Key_Eisu_Shift,
QtCore.Qt.Key_Messenger,
QtCore.Qt.Key_Paste,
QtCore.Qt.Key_Sleep,
QtCore.Qt.Key_KeyboardLightOnOff,
QtCore.Qt.Key_Hangul_Start,
QtCore.Qt.Key_Codeinput,
QtCore.Qt.Key_Yes,
QtCore.Qt.Key_Context4,
QtCore.Qt.Key_Context3,
QtCore.Qt.Key_Context2,
QtCore.Qt.Key_Context1,
QtCore.Qt.Key_BrightnessAdjust,
QtCore.Qt.Key_SingleCandidate,
QtCore.Qt.Key_Dead_Abovering,
QtCore.Qt.Key_Finance,
QtCore.Qt.Key_KeyboardBrightnessDown,
QtCore.Qt.Key_Dead_Breve,
QtCore.Qt.Key_Kanji,
QtCore.Qt.Key_Eject,
QtCore.Qt.Key_Copy,
QtCore.Qt.Key_Display,
QtCore.Qt.Key_WWW,
QtCore.Qt.Key_HotLinks,
QtCore.Qt.Key_Cut,
QtCore.Qt.Key_CameraFocus,
QtCore.Qt.Key_Dead_Macron,
QtCore.Qt.Key_RotationPB,
QtCore.Qt.Key_Hibernate,
QtCore.Qt.Key_Select,
QtCore.Qt.Key_Dead_Diaeresis,
QtCore.Qt.Key_PowerDown,
QtCore.Qt.Key_Shop,
QtCore.Qt.Key_WakeUp,
QtCore.Qt.Key_Pictures,
QtCore.Qt.Key_Zenkaku_Hankaku,
QtCore.Qt.Key_Play,
QtCore.Qt.Key_MySites,
QtCore.Qt.Key_VoiceDial,
QtCore.Qt.Key_Dead_Grave,
QtCore.Qt.Key_History,
QtCore.Qt.Key_Dead_Acute,
QtCore.Qt.Key_AudioRepeat,
QtCore.Qt.Key_Calendar,
QtCore.Qt.Key_ContrastAdjust,
QtCore.Qt.Key_AudioCycleTrack,
QtCore.Qt.Key_Meeting,
QtCore.Qt.Key_Terminal,
QtCore.Qt.Key_unknown,
QtCore.Qt.Key_iTouch,
QtCore.Qt.Key_Camera,
QtCore.Qt.Key_Flip,
QtCore.Qt.Key_Kana_Shift,
QtCore.Qt.Key_Battery,
QtCore.Qt.Key_Henkan,
QtCore.Qt.Key_Tools,
QtCore.Qt.Key_Cancel,
QtCore.Qt.Key_Hangul_PostHanja,
QtCore.Qt.Key_Hangul,
QtCore.Qt.Key_Hangup,
QtCore.Qt.Key_ZoomOut,
QtCore.Qt.Key_AddFavorite,
QtCore.Qt.Key_Dead_Iota,
QtCore.Qt.Key_Support,
QtCore.Qt.Key_Documents,
QtCore.Qt.Key_PowerOff,
QtCore.Qt.Key_Explorer,
QtCore.Qt.Key_RotateWindows,
QtCore.Qt.Key_MonBrightnessDown,
QtCore.Qt.Key_View,
QtCore.Qt.Key_Reload,
QtCore.Qt.Key_WLAN,
QtCore.Qt.Key_Dead_Hook,
QtCore.Qt.Key_News,
QtCore.Qt.Key_LogOff,
QtCore.Qt.Key_Word,
QtCore.Qt.Key_Romaji,
QtCore.Qt.Key_Time,
QtCore.Qt.Key_Bluetooth,
QtCore.Qt.Key_Dead_Cedilla,
QtCore.Qt.Key_ZoomIn,
QtCore.Qt.Key_Reply,
QtCore.Qt.Key_Dead_Ogonek,
QtCore.Qt.Key_Music,
QtCore.Qt.Key_Hiragana_Katakana,
QtCore.Qt.Key_CD,
QtCore.Qt.Key_Execute,
QtCore.Qt.Key_Memo,
QtCore.Qt.Key_No,
QtCore.Qt.Key_Book,
QtCore.Qt.Key_MonBrightnessUp,
QtCore.Qt.Key_Dead_Doubleacute,
QtCore.Qt.Key_MultipleCandidate,
QtCore.Qt.Key_TopMenu,
QtCore.Qt.Key_Touroku,
QtCore.Qt.Key_Massyo,
QtCore.Qt.Key_MediaLast,
QtCore.Qt.Key_Hangul_End,
QtCore.Qt.Key_RotationKB,
QtCore.Qt.Key_Spell,
QtCore.Qt.Key_ToDoList,
QtCore.Qt.Key_SplitScreen,
QtCore.Qt.Key_PreviousCandidate,
QtCore.Qt.Key_Dead_Abovedot,
QtCore.Qt.Key_BackForward,
QtCore.Qt.Key_Dead_Circumflex,
QtCore.Qt.Key_ToggleCallHangup,
QtCore.Qt.Key_AudioRandomPlay,
QtCore.Qt.Key_Mode_switch,
QtCore.Qt.Key_Close,
QtCore.Qt.Key_Go,
]

already_tested = [
QtCore.Qt.Key.Key_ordfeminine,
QtCore.Qt.Key.Key_Ampersand,
QtCore.Qt.Key.Key_currency,
QtCore.Qt.Key.Key_BracketRight,
QtCore.Qt.Key.Key_Up,
QtCore.Qt.Key.Key_Plus,
QtCore.Qt.Key.Key_AsciiCircum,
QtCore.Qt.Key.Key_MediaPlay,
QtCore.Qt.Key.Key_Help,
QtCore.Qt.Key.Key_Tab,
QtCore.Qt.Key.Key_Percent,
QtCore.Qt.Key.Key_brokenbar,
QtCore.Qt.Key.Key_Direction_R,
QtCore.Qt.Key.Key_Print,
QtCore.Qt.Key.Key_Direction_L,
QtCore.Qt.Key.Key_Aacute,
QtCore.Qt.Key.Key_diaeresis,
QtCore.Qt.Key.Key_Home,
QtCore.Qt.Key.Key_Hyper_L,
QtCore.Qt.Key.Key_THORN,
QtCore.Qt.Key.Key_Delete,
QtCore.Qt.Key.Key_registered,
QtCore.Qt.Key.Key_Hyper_R,
QtCore.Qt.Key.Key_MediaPrevious,
QtCore.Qt.Key.Key_ssharp,
QtCore.Qt.Key.Key_guillemotleft,
QtCore.Qt.Key.Key_Q,
QtCore.Qt.Key.Key_Slash,
QtCore.Qt.Key.Key_ParenLeft,
QtCore.Qt.Key.Key_Iacute,
QtCore.Qt.Key.Key_onehalf,
QtCore.Qt.Key.Key_Clear,
QtCore.Qt.Key.Key_Udiaeresis,
QtCore.Qt.Key.Key_onesuperior,
QtCore.Qt.Key.Key_MediaStop,
QtCore.Qt.Key.Key_Ocircumflex,
QtCore.Qt.Key.Key_Right,
QtCore.Qt.Key.Key_paragraph,
QtCore.Qt.Key.Key_Down,
QtCore.Qt.Key.Key_QuoteDbl,
QtCore.Qt.Key.Key_Backspace,
QtCore.Qt.Key.Key_Yacute,
QtCore.Qt.Key.Key_Atilde,
QtCore.Qt.Key.Key_ETH,
QtCore.Qt.Key.Key_Ecircumflex,
QtCore.Qt.Key.Key_PageUp,
QtCore.Qt.Key.Key_cedilla,
QtCore.Qt.Key.Key_F18,
QtCore.Qt.Key.Key_F19,
QtCore.Qt.Key.Key_F16,
QtCore.Qt.Key.Key_F17,
QtCore.Qt.Key.Key_F14,
QtCore.Qt.Key.Key_F15,
QtCore.Qt.Key.Key_F12,
QtCore.Qt.Key.Key_F13,
QtCore.Qt.Key.Key_F10,
QtCore.Qt.Key.Key_F11,
QtCore.Qt.Key.Key_Back,
QtCore.Qt.Key.Key_Control,
QtCore.Qt.Key.Key_Ucircumflex,
QtCore.Qt.Key.Key_5,
QtCore.Qt.Key.Key_4,
QtCore.Qt.Key.Key_7,
QtCore.Qt.Key.Key_6,
QtCore.Qt.Key.Key_1,
QtCore.Qt.Key.Key_0,
QtCore.Qt.Key.Key_3,
QtCore.Qt.Key.Key_2,
QtCore.Qt.Key.Key_9,
QtCore.Qt.Key.Key_8,
QtCore.Qt.Key.Key_E,
QtCore.Qt.Key.Key_D,
QtCore.Qt.Key.Key_G,
QtCore.Qt.Key.Key_F,
QtCore.Qt.Key.Key_A,
QtCore.Qt.Key.Key_division,
QtCore.Qt.Key.Key_C,
QtCore.Qt.Key.Key_B,
QtCore.Qt.Key.Key_M,
QtCore.Qt.Key.Key_L,
QtCore.Qt.Key.Key_O,
QtCore.Qt.Key.Key_N,
QtCore.Qt.Key.Key_I,
QtCore.Qt.Key.Key_Semicolon,
QtCore.Qt.Key.Key_K,
QtCore.Qt.Key.Key_J,
QtCore.Qt.Key.Key_U,
QtCore.Qt.Key.Key_T,
QtCore.Qt.Key.Key_W,
QtCore.Qt.Key.Key_V,
QtCore.Qt.Key.Key_MediaRecord,
QtCore.Qt.Key.Key_P,
QtCore.Qt.Key.Key_S,
QtCore.Qt.Key.Key_R,
QtCore.Qt.Key.Key_Y,
QtCore.Qt.Key.Key_X,
QtCore.Qt.Key.Key_Z,
QtCore.Qt.Key.Key_F4,
QtCore.Qt.Key.Key_F5,
QtCore.Qt.Key.Key_F6,
QtCore.Qt.Key.Key_F7,
QtCore.Qt.Key.Key_F1,
QtCore.Qt.Key.Key_F2,
QtCore.Qt.Key.Key_F3,
QtCore.Qt.Key.Key_F8,
QtCore.Qt.Key.Key_F9,
QtCore.Qt.Key.Key_Odiaeresis,
QtCore.Qt.Key.Key_Escape,
QtCore.Qt.Key.Key_ydiaeresis,
QtCore.Qt.Key.Key_Meta,
QtCore.Qt.Key.Key_Egrave,
QtCore.Qt.Key.Key_nobreakspace,
QtCore.Qt.Key.Key_degree,
QtCore.Qt.Key.Key_BraceLeft,
QtCore.Qt.Key.Key_threesuperior,
QtCore.Qt.Key.Key_mu,
QtCore.Qt.Key.Key_SysReq,
QtCore.Qt.Key.Key_Menu,
QtCore.Qt.Key.Key_Bar,
QtCore.Qt.Key.Key_Backtab,
QtCore.Qt.Key.Key_multiply,
QtCore.Qt.Key.Key_CapsLock,
QtCore.Qt.Key.Key_Aring,
QtCore.Qt.Key.Key_PageDown,
QtCore.Qt.Key.Key_threequarters,
QtCore.Qt.Key.Key_copyright,
QtCore.Qt.Key.Key_Asterisk,
QtCore.Qt.Key.Key_Eacute,
QtCore.Qt.Key.Key_periodcentered,
QtCore.Qt.Key.Key_MediaNext,
QtCore.Qt.Key.Key_Search,
QtCore.Qt.Key.Key_Igrave,
QtCore.Qt.Key.Key_Acircumflex,
QtCore.Qt.Key.Key_Icircumflex,
QtCore.Qt.Key.Key_Agrave,
QtCore.Qt.Key.Key_Idiaeresis,
QtCore.Qt.Key.Key_acute,
QtCore.Qt.Key.Key_Return,
QtCore.Qt.Key.Key_BracketLeft,
QtCore.Qt.Key.Key_Minus,
QtCore.Qt.Key.Key_Apostrophe,
QtCore.Qt.Key.Key_Adiaeresis,
QtCore.Qt.Key.Key_LaunchMail,
QtCore.Qt.Key.Key_End,
QtCore.Qt.Key.Key_Otilde,
QtCore.Qt.Key.Key_TrebleUp,
QtCore.Qt.Key.Key_BassUp,
QtCore.Qt.Key.Key_Ntilde,
QtCore.Qt.Key.Key_Uacute,
QtCore.Qt.Key.Key_sterling,
QtCore.Qt.Key.Key_hyphen,
QtCore.Qt.Key.Key_Space,
QtCore.Qt.Key.Key_Pause,
QtCore.Qt.Key.Key_F27,
QtCore.Qt.Key.Key_F26,
QtCore.Qt.Key.Key_F25,
QtCore.Qt.Key.Key_F24,
QtCore.Qt.Key.Key_F23,
QtCore.Qt.Key.Key_F22,
QtCore.Qt.Key.Key_F21,
QtCore.Qt.Key.Key_F20,
QtCore.Qt.Key.Key_F29,
QtCore.Qt.Key.Key_F28,
QtCore.Qt.Key.Key_OpenUrl,
QtCore.Qt.Key.Key_Launch8,
QtCore.Qt.Key.Key_Launch9,
QtCore.Qt.Key.Key_onequarter,
QtCore.Qt.Key.Key_HomePage,
QtCore.Qt.Key.Key_Launch1,
QtCore.Qt.Key.Key_Launch2,
QtCore.Qt.Key.Key_Launch3,
QtCore.Qt.Key.Key_Launch4,
QtCore.Qt.Key.Key_Launch5,
QtCore.Qt.Key.Key_Launch6,
QtCore.Qt.Key.Key_Launch7,
QtCore.Qt.Key.Key_Ediaeresis,
QtCore.Qt.Key.Key_Shift,
QtCore.Qt.Key.Key_LaunchA,
QtCore.Qt.Key.Key_LaunchB,
QtCore.Qt.Key.Key_LaunchC,
QtCore.Qt.Key.Key_LaunchD,
QtCore.Qt.Key.Key_LaunchE,
QtCore.Qt.Key.Key_LaunchF,
QtCore.Qt.Key.Key_Left,
QtCore.Qt.Key.Key_Period,
QtCore.Qt.Key.Key_Ooblique,
QtCore.Qt.Key.Key_Colon,
QtCore.Qt.Key.Key_Forward,
QtCore.Qt.Key.Key_Greater,
QtCore.Qt.Key.Key_VolumeMute,
QtCore.Qt.Key.Key_ParenRight,
QtCore.Qt.Key.Key_Oacute,
QtCore.Qt.Key.Key_NumLock,
QtCore.Qt.Key.Key_macron,
QtCore.Qt.Key.Key_section,
QtCore.Qt.Key.Key_Equal,
QtCore.Qt.Key.Key_Standby,
QtCore.Qt.Key.Key_TrebleDown,
QtCore.Qt.Key.Key_Launch0,
QtCore.Qt.Key.Key_Enter,
QtCore.Qt.Key.Key_Less,
QtCore.Qt.Key.Key_Alt,
QtCore.Qt.Key.Key_yen,
QtCore.Qt.Key.Key_NumberSign,
QtCore.Qt.Key.Key_twosuperior,
QtCore.Qt.Key.Key_Favorites,
QtCore.Qt.Key.Key_Exclam,
QtCore.Qt.Key.Key_Insert,
QtCore.Qt.Key.Key_guillemotright,
QtCore.Qt.Key.Key_VolumeDown,
QtCore.Qt.Key.Key_ScrollLock,
QtCore.Qt.Key.Key_BassDown,
QtCore.Qt.Key.Key_BassBoost,
QtCore.Qt.Key.Key_masculine,
QtCore.Qt.Key.Key_H,
QtCore.Qt.Key.Key_Refresh,
QtCore.Qt.Key.Key_Super_R,
QtCore.Qt.Key.Key_F34,
QtCore.Qt.Key.Key_F35,
QtCore.Qt.Key.Key_F30,
QtCore.Qt.Key.Key_F31,
QtCore.Qt.Key.Key_F32,
QtCore.Qt.Key.Key_F33,
QtCore.Qt.Key.Key_Super_L,
QtCore.Qt.Key.Key_Dollar,
QtCore.Qt.Key.Key_Backslash,
QtCore.Qt.Key.Key_At,
QtCore.Qt.Key.Key_Comma,
QtCore.Qt.Key.Key_notsign,
QtCore.Qt.Key.Key_questiondown,
QtCore.Qt.Key.Key_QuoteLeft,
QtCore.Qt.Key.Key_cent,
QtCore.Qt.Key.Key_BraceRight,
QtCore.Qt.Key.Key_Stop,
QtCore.Qt.Key.Key_VolumeUp,
QtCore.Qt.Key.Key_Ograve,
QtCore.Qt.Key.Key_LaunchMedia,
QtCore.Qt.Key.Key_exclamdown,
QtCore.Qt.Key.Key_plusminus,
QtCore.Qt.Key.Key_Question,
QtCore.Qt.Key.Key_AsciiTilde,
QtCore.Qt.Key.Key_Underscore,
]
for k in QtCore.Qt.Key.values.values():
	# if k in already_tested:
	# 	continue
	if k in ignored_keys:
		continue
	a = QtTest.QTest.keyToAscii(k)
	if a == b'\x00':
		continue

	try:
		a = str(a).decode('ascii')
	except UnicodeDecodeError:
		continue

	print k, a


"""
PySide.QtCore.Qt.Key.Key_Space
PySide.QtCore.Qt.Key.Key_Period .
PySide.QtCore.Qt.Key.Key_Colon :
PySide.QtCore.Qt.Key.Key_Greater >
PySide.QtCore.Qt.Key.Key_ParenRight )
PySide.QtCore.Qt.Key.Key_Equal =
PySide.QtCore.Qt.Key.Key_Enter
PySide.QtCore.Qt.Key.Key_Less <
PySide.QtCore.Qt.Key.Key_NumberSign #
PySide.QtCore.Qt.Key.Key_Exclam !
PySide.QtCore.Qt.Key.Key_H h
PySide.QtCore.Qt.Key.Key_Dollar $
PySide.QtCore.Qt.Key.Key_Backslash \
PySide.QtCore.Qt.Key.Key_At @
PySide.QtCore.Qt.Key.Key_Comma ,
PySide.QtCore.Qt.Key.Key_QuoteLeft `
PySide.QtCore.Qt.Key.Key_BraceRight }
PySide.QtCore.Qt.Key.Key_Question ?
PySide.QtCore.Qt.Key.Key_AsciiTilde ~
PySide.QtCore.Qt.Key.Key_Underscore _
PySide.QtCore.Qt.Key.Key_Return
PySide.QtCore.Qt.Key.Key_BracketLeft [
PySide.QtCore.Qt.Key.Key_Minus -
PySide.QtCore.Qt.Key.Key_Apostrophe '
PySide.QtCore.Qt.Key.Key_Bar |
PySide.QtCore.Qt.Key.Key_Backtab 
PySide.QtCore.Qt.Key.Key_Asterisk *
PySide.QtCore.Qt.Key.Key_Any
PySide.QtCore.Qt.Key.Key_5 5
PySide.QtCore.Qt.Key.Key_4 4
PySide.QtCore.Qt.Key.Key_7 7
PySide.QtCore.Qt.Key.Key_6 6
PySide.QtCore.Qt.Key.Key_1 1
PySide.QtCore.Qt.Key.Key_0 0
PySide.QtCore.Qt.Key.Key_3 3
PySide.QtCore.Qt.Key.Key_2 2
PySide.QtCore.Qt.Key.Key_9 9
PySide.QtCore.Qt.Key.Key_8 8
PySide.QtCore.Qt.Key.Key_E e
PySide.QtCore.Qt.Key.Key_D d
PySide.QtCore.Qt.Key.Key_G g
PySide.QtCore.Qt.Key.Key_F f
PySide.QtCore.Qt.Key.Key_A a
PySide.QtCore.Qt.Key.Key_C c
PySide.QtCore.Qt.Key.Key_B b
PySide.QtCore.Qt.Key.Key_M m
PySide.QtCore.Qt.Key.Key_L l
PySide.QtCore.Qt.Key.Key_O o
PySide.QtCore.Qt.Key.Key_N n
PySide.QtCore.Qt.Key.Key_I i
PySide.QtCore.Qt.Key.Key_Semicolon ;
PySide.QtCore.Qt.Key.Key_K k
PySide.QtCore.Qt.Key.Key_J j
PySide.QtCore.Qt.Key.Key_U u
PySide.QtCore.Qt.Key.Key_T t
PySide.QtCore.Qt.Key.Key_W w
PySide.QtCore.Qt.Key.Key_V v
PySide.QtCore.Qt.Key.Key_P p
PySide.QtCore.Qt.Key.Key_S s
PySide.QtCore.Qt.Key.Key_R r
PySide.QtCore.Qt.Key.Key_Y y
PySide.QtCore.Qt.Key.Key_X x
PySide.QtCore.Qt.Key.Key_Z z
PySide.QtCore.Qt.Key.Key_Escape 
PySide.QtCore.Qt.Key.Key_BraceLeft {
PySide.QtCore.Qt.Key.Key_Slash /
PySide.QtCore.Qt.Key.Key_ParenLeft (
PySide.QtCore.Qt.Key.Key_QuoteDbl "
PySide.QtCore.Qt.Key.Key_Backspace 
PySide.QtCore.Qt.Key.Key_Ampersand &
PySide.QtCore.Qt.Key.Key_BracketRight ]
PySide.QtCore.Qt.Key.Key_Plus +
PySide.QtCore.Qt.Key.Key_AsciiCircum ^
PySide.QtCore.Qt.Key.Key_Tab
PySide.QtCore.Qt.Key.Key_Percent %
PySide.QtCore.Qt.Key.Key_Q q
"""