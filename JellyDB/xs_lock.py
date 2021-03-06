from __future__ import annotations
import threading
import traceback

class XSLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._share_count = 0
        self._exclusive_count = 0
    
    def __enter__(self):
        # Used with `with` statement. The lock will already have been acquired when this is called.
        return self

    def __exit__(self, exception_type, exception_value, __traceback):
        self.release()
    
    """
    # Called when pickled (warning, this does not change any counters)
    # https://stackoverflow.com/questions/50441786/pickle-cant-pickle-thread-lock-objects
    """
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_lock']
        return state
    
    """
    # Called when unpickled (warning, this does not change any counters)
    """
    def __setstate__(self, state):
        self.__dict__.update(state)
        self._lock = threading.Lock()
    
    # Returns itself
    def acquire_X(self) -> XSLock:
        if self.acquire_X_bool() == False:
            raise Exception("Could not acquire exclusive lock")
        return self
    
    # Returns itself
    def acquire_S(self) -> XSLock:
        if self.acquire_S_bool() == False:
            raise Exception("Could not acquire shared lock")
        return self
    
    # Returns success of acquiring exclusive lock
    def acquire_X_bool(self) -> bool:
        with self._lock:
            if self._share_count > 0 or self._exclusive_count > 0:
                return False
            self._exclusive_count = 1
            return True
    
    # Returns success of acquiring shared lock
    def acquire_S_bool(self) -> bool:
        with self._lock:
            if self._exclusive_count > 0:
                return False
            self._share_count += 1
            return True
    
    # Releases one lock - inferring which kind to release.
    def release(self):
        with self._lock:
            if self._share_count > 0:
                self._share_count -= 1
            elif self._exclusive_count > 0:
                self._exclusive_count = 0
            else:
                raise Exception("There are no S or X locks to release")

    def upgrade(self) -> XSLock:
        with self._lock:
            if self._share_count != 1 or self._exclusive_count != 0:
                raise Exception("Cannot upgrade lock; there are {} sharers and {} exclusive holders of this lock".format(self._share_count, self._exclusive_count))
                return False
            self._share_count = 0
            self._exclusive_count = 1
            return self
