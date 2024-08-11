from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    overload,
)

from agentifyme.base_config import BaseConfig, BaseModule
from agentifyme.logger import get_logger
from agentifyme.utilities.func_utils import (
    Param,
    execute_function,
    get_function_metadata,
)

logger = get_logger()


class TaskError(Exception):
    pass


class TaskConfig(BaseConfig):
    """
    Represents the configuration for a task.

    Attributes:
        name (str): The name of the task.
        description (str): The description of the task.
        objective (Optional[str]): The objective of the task.
        instructions (Optional[str]): The instructions for completing the task.
        tools (Optional[List[Tool]]): The list of tools required for the task.
        input_params (List[Param]): The list of input parameters for the task.
        output_params (List[Param]): The list of output parameters for the task.
    """

    objective: Optional[str] = None
    instructions: Optional[str] = None
    # tools: Optional[List[Tool]]
    input_parameters: Dict[str, Param]
    output_parameters: List[Param]


class Task(BaseModule):
    def __init__(self, config: TaskConfig, *args, **kwargs) -> None:
        super().__init__(config, **kwargs)
        self.config = config

    def run(self, *args, **kwargs: Any) -> Any:
        logger.info(f"Running task: {self.config.name}")
        if self.config.func:
            kwargs.update(zip(self.config.func.__code__.co_varnames, args))
            result = execute_function(self.config.func, kwargs)
            return result
        else:
            raise NotImplementedError("Task function not implemented")


@overload
def task(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator function for defining a workflow."""


@overload
def task(*, name: str, description: Optional[str] = None) -> Callable[..., Any]: ...


def task(
    func: Union[Callable[..., Any], None] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    objective: Optional[str] = None,
    instructions: Optional[str] = None,
    # tools: Optional[List[Tool]] = None,
) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_metadata = get_function_metadata(func)
        task_config = TaskConfig(
            name=func_metadata.name,
            description=description or func_metadata.description,
            input_parameters=func_metadata.input_parameters,
            output_parameters=func_metadata.output_parameters,
            objective=objective,
            instructions=instructions,
            func=func,
            # tools=tools,
        )

        _task_instance = Task(task_config)
        TaskConfig.register(_task_instance)

        def wrapper(*args, **kwargs) -> Any:
            kwargs.update(zip(func.__code__.co_varnames, args))
            result = _task_instance(**kwargs)
            return result

        # pylint: disable=protected-access
        wrapper.__agentifyme = _task_instance  # type: ignore

        return wrapper

    if callable(func):
        return decorator(func)
    elif name is not None:

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            return decorator(func)

        return decorator
    else:
        raise TaskError("Invalid arguments for workflow decorator")
