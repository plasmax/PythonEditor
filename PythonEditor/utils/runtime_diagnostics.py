from __future__ import print_function
import os
import sys
import threading

from PythonEditor.utils.log import logger, LOG_PATH


_INSTALLED = False
_ORIGINAL_SYS_EXCEPTHOOK = None
_ORIGINAL_THREADING_EXCEPTHOOK = None


def _format_widget(widget):
    if widget is None:
        return 'None'
    try:
        name = widget.objectName()
    except Exception:
        name = ''
    try:
        title = widget.windowTitle()
    except Exception:
        title = ''
    return '%s(objectName=%r, title=%r)' % (widget.__class__.__name__, name, title)


def _qt_context():
    try:
        from PythonEditor.ui.Qt import QtWidgets
    except Exception:
        return 'QtWidgets unavailable'

    app = QtWidgets.QApplication.instance()
    if app is None:
        return 'QApplication: None'

    try:
        active = app.activeWindow()
    except Exception:
        active = None
    try:
        focus = app.focusWidget()
    except Exception:
        focus = None
    try:
        top_level = app.topLevelWidgets()
    except Exception:
        top_level = []

    top_summary = ', '.join(_format_widget(w) for w in top_level[:8]) or 'None'
    if len(top_level) > 8:
        top_summary += ', ... (+%d more)' % (len(top_level) - 8)

    return 'activeWindow=%s; focusWidget=%s; topLevel=%s' % (
        _format_widget(active),
        _format_widget(focus),
        top_summary
    )


def _log_exception(exc_type, exc, tb, source):
    try:
        logger.error('Unhandled exception (%s)', source)
        logger.error('Thread: %s', threading.current_thread().name)
        logger.error('CWD: %s', os.getcwd())
        logger.error('Args: %s', sys.argv)
        logger.error('QT_PREFERRED_BINDING: %s', os.getenv('QT_PREFERRED_BINDING'))
        logger.error('Qt context: %s', _qt_context())
        logger.error('Log file: %s', LOG_PATH)
        logger.error('Traceback:', exc_info=(exc_type, exc, tb))
    except Exception:
        pass


def _sys_excepthook(exc_type, exc, tb):
    _log_exception(exc_type, exc, tb, 'sys.excepthook')
    if _ORIGINAL_SYS_EXCEPTHOOK and _ORIGINAL_SYS_EXCEPTHOOK is not _sys_excepthook:
        _ORIGINAL_SYS_EXCEPTHOOK(exc_type, exc, tb)


def _thread_excepthook(args):
    _log_exception(args.exc_type, args.exc_value, args.exc_traceback, 'threading.excepthook')
    if _ORIGINAL_THREADING_EXCEPTHOOK and _ORIGINAL_THREADING_EXCEPTHOOK is not _thread_excepthook:
        _ORIGINAL_THREADING_EXCEPTHOOK(args)


def _qt_message_level(msg_type):
    try:
        from PythonEditor.ui.Qt import QtCore
    except Exception:
        return logger.info

    qt_msg_type = getattr(QtCore, 'QtMsgType', None)
    if qt_msg_type is None:
        return logger.info

    try:
        if msg_type == qt_msg_type.QtDebugMsg:
            return logger.debug
        if hasattr(qt_msg_type, 'QtInfoMsg') and msg_type == qt_msg_type.QtInfoMsg:
            return logger.info
        if msg_type == qt_msg_type.QtWarningMsg:
            return logger.warning
        if msg_type == qt_msg_type.QtCriticalMsg:
            return logger.error
        if msg_type == qt_msg_type.QtFatalMsg:
            return logger.critical
    except Exception:
        pass

    return logger.info


def _format_qt_message_context(context):
    if context is None:
        return ''
    try:
        filename = context.file
        line = context.line
        function = context.function
    except Exception:
        return ''

    if isinstance(filename, bytes):
        filename = filename.decode(errors='replace')
    if isinstance(function, bytes):
        function = function.decode(errors='replace')

    return ' (%s:%s %s)' % (filename, line, function)


def _install_qt_message_handler():
    try:
        from PythonEditor.ui.Qt import QtCore
    except Exception:
        return False

    install = getattr(QtCore, 'qInstallMessageHandler', None)
    if install is None:
        install = getattr(QtCore, 'qInstallMsgHandler', None)
    if install is None:
        return False

    def handler(*args):
        if len(args) == 3:
            msg_type, context, message = args
        elif len(args) == 2:
            msg_type, message = args
            context = None
        else:
            return

        if isinstance(message, bytes):
            message = message.decode(errors='replace')

        ctx = _format_qt_message_context(context)
        log_fn = _qt_message_level(msg_type)
        log_fn('Qt%s: %s', ctx, message)

    try:
        install(handler)
        return True
    except Exception:
        logger.exception('Failed to install Qt message handler')
        return False


def install():
    global _INSTALLED
    global _ORIGINAL_SYS_EXCEPTHOOK
    global _ORIGINAL_THREADING_EXCEPTHOOK

    if _INSTALLED:
        return

    _INSTALLED = True
    _ORIGINAL_SYS_EXCEPTHOOK = sys.excepthook
    sys.excepthook = _sys_excepthook

    if hasattr(threading, 'excepthook'):
        _ORIGINAL_THREADING_EXCEPTHOOK = threading.excepthook
        threading.excepthook = _thread_excepthook

    _install_qt_message_handler()
    logger.info('Runtime diagnostics enabled. Log file: %s', LOG_PATH)
