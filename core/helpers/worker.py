from PySide6.QtCore import QThread, Signal
from core.helpers.utils import get_logger

logger = get_logger()

class SeleniumWorker(QThread):
    """Worker Thread kết nối Selenium Engine với giao diện PySide6 (chống treo UI)"""
    log_signal = Signal(str)
    progress_signal = Signal(int)
    result_signal = Signal(dict)
    finished_signal = Signal(bool)

    def __init__(self, runner_func, *args, **kwargs):
        super().__init__()
        self.runner_func = runner_func
        self.args = args
        self.kwargs = kwargs
        self._is_stopped = False

    def run(self):
        try:
            self.log_signal.emit("[WORKER] Bắt đầu tiến trình kiểm thử ngầm...")
            self.progress_signal.emit(10)
            
            # Truyền worker vào runner để callback progress/log
            results = self.runner_func(worker=self, *self.args, **self.kwargs)
            
            self.progress_signal.emit(100)
            self.result_signal.emit(results if results else {"status": "SUCCESS"})
        except Exception as e:
            logger.error(f"[WORKER ERROR] {str(e)}")
            self.log_signal.emit(f"[ERROR] {str(e)}")
            self.result_signal.emit({"status": "FAILED", "error": str(e)})
        finally:
            self.finished_signal.emit(True)

    def stop(self):
        self._is_stopped = True