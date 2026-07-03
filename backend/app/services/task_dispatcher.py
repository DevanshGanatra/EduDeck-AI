from abc import ABC, abstractmethod
from typing import Callable, Any
from fastapi import BackgroundTasks

class TaskDispatcher(ABC):
    @abstractmethod
    def dispatch(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        pass

class FastAPITaskDispatcher(TaskDispatcher):
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def dispatch(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.background_tasks.add_task(func, *args, **kwargs)
