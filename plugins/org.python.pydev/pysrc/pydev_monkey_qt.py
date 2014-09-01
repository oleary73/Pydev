from __future__ import nested_scopes

import _pydev_threading as threading
from pydevd_constants import STATE_RUN
import sys
import pydevd_tracing
from pydevd_comm import GetGlobalDebugger

threadingCurrentThread = threading.currentThread


def set_trace_in_qt():
    debugger = GetGlobalDebugger()
    if debugger is not None:
        pydevd_tracing.SetTrace(debugger.trace_dispatch)
        
    
        
def remove_trace_in_qt():
    debugger = GetGlobalDebugger()
    if debugger is not None:
        pydevd_tracing.SetTrace(None)
        
    frame = sys._getframe()
    while frame is not None:
        frame.f_trace = None
        frame = frame.f_back
        
    t = threadingCurrentThread()
    additional_info = t.additionalInfo
    additional_info.pydev_state = STATE_RUN
    additional_info.pydev_step_stop = None
    additional_info.pydev_step_cmd = None
    additional_info.pydev_smart_step_stop = None
    additional_info.pydev_django_resolve_frame = None

        
        
_patched_qt = False
def patch_qt():
    '''
    This method patches qt (PySide or PyQt4) so that we have hooks to set the tracing for QThread.
    '''
    
    # Avoid patching more than once
    global _patched_qt
    if _patched_qt:
        return
    
    _patched_qt = True
    
    try:
        from PySide import QtCore
    except:
        try:
            from PyQt4 import QtCore
        except:
            return
    
    _original_thread_init = QtCore.QThread.__init__
    _original_runnable_init = QtCore.QRunnable.__init__
    
    
    class FuncWrapper:
        
        def __init__(self, original):
            self._original = original
        
        def __call__(self, *args, **kwargs):
            set_trace_in_qt()
            try:
                return self._original(*args, **kwargs)
            finally:
                remove_trace_in_qt()
    
    class StartedSignalWrapper:  # Wrapper for the QThread.started signal
        
        def __init__(self, thread, original_started):
            self.thread = thread
            self.original_started = original_started
            
        def connect(self, func, *args, **kwargs):
            return self.original_started.connect(FuncWrapper(func), *args, **kwargs)
        
        def disconnect(self, *args, **kwargs):
            return self.original_started.disconnect(*args, **kwargs)
        
        def emit(self, *args, **kwargs):
            return self.original_started.emit(*args, **kwargs)
            
    
    class ThreadWrapper(QtCore.QThread):  # Wrapper for QThread
        
        def __init__(self, *args, **kwargs):
            _original_thread_init(self)
    
            self._original_run = self.run
            self.run = self._new_run
            self._original_started = self.started
            self.started = StartedSignalWrapper(self, self.started)
            
        def _new_run(self):
            set_trace_in_qt()
            try:
                return self._original_run()
            finally:
                remove_trace_in_qt()
    
    class RunnableWrapper(QtCore.QRunnable):  # Wrapper for QRunnable
        
        def __init__(self, *args, **kwargs):
            _original_runnable_init(self)
    
            self._original_run = self.run
            self.run = self._new_run
            
            
        def _new_run(self):
            set_trace_in_qt()
            try:
                return self._original_run()
            finally:
                remove_trace_in_qt()
            
    QtCore.QThread = ThreadWrapper
    QtCore.QRunnable = RunnableWrapper
