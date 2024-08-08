import ast
import inspect
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
)
from uuid import UUID

from docstring_parser import Docstring, parse
from pydantic import BaseModel, Field, ValidationError


class Param(BaseModel):
    """
    Represents a parameter.

    Attributes:
        name (str): The name of the parameter.
        description (str): The description of the parameter.
        data_type (str): The data type of the parameter.
        default_value (Any): The default value of the parameter. Defaults to None.
        required (bool): Whether the parameter is required. Defaults to True.
    """

    name: str
    description: str
    data_type: str
    default_value: Any = None
    required: bool = False
    class_name: Optional[str] = None
    nested_fields: Dict[str, "Param"] = {}


class FunctionMetadata(BaseModel):
    """
    Represents metadata for a function.

    Attributes:
        name (str): The name of the function.
        description (str): The description of the function.
        input_params (List[Param]): The input parameters of the function.
        output_params (List[Param]): The output parameters of the function.
        doc_string (str): The docstring of the function.
    """

    name: str
    description: str
    input_parameters: Dict[str, Param]
    output_parameters: List[Param]
    doc_string: str


def json_datatype_from_python_type(python_type: Any) -> str:
    # Boolean type
    if python_type is bool:
        return "boolean"

    # Handle Optional types
    origin = get_origin(python_type)
    if origin is Union:
        args = get_args(python_type)
        if len(args) == 2 and type(None) in args:
            # This is an Optional type
            return json_datatype_from_python_type(
                [arg for arg in args if arg is not type(None)][0]
            )

    # Handle List types
    if origin in (list, List) or (
        isinstance(python_type, type) and issubclass(python_type, list)
    ):
        return "array"

    # Handle Dict types
    if origin in (dict, Dict) or (
        isinstance(python_type, type) and issubclass(python_type, dict)
    ):
        return "object"

    # Handle primitive types and BaseModel
    if isinstance(python_type, type):
        if issubclass(python_type, str):
            return "string"
        if issubclass(python_type, (int, float)):
            return "number"
        if issubclass(python_type, bool):
            return "boolean"
        if issubclass(python_type, BaseModel):
            return "object"

    # Handle Any type
    if python_type is Any:
        return "object"

    # Default case
    return "string"


def get_pydantic_fields(
    model: Type[BaseModel],
    parsed_docstring: Optional[Docstring] = None,
    is_output: bool = False,
) -> Dict[str, Param]:
    fields = {}
    for name, field in model.model_fields.items():
        field_type = field.annotation
        field_description = ""

        if parsed_docstring and not is_output:
            field_description = next(
                (p.description for p in parsed_docstring.params if p.arg_name == name),
                "",
            )

        if field_description is None:
            field_description = ""

        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            nested_fields = get_pydantic_fields(field_type, parsed_docstring, is_output)
            fields[name] = Param(
                name=name,
                description=field_description,
                data_type="object",
                required=field.is_required(),
                nested_fields=nested_fields,
            )
        else:
            fields[name] = Param(
                name=name,
                description=field_description,
                data_type=json_datatype_from_python_type(field_type),
                default_value=field.default if not field.is_required() else None,
                required=field.is_required(),
            )
    return fields


def get_input_parameters(
    func: Callable, parsed_docstring: Docstring
) -> Dict[str, Param]:
    sig = inspect.signature(func)
    input_parameters = {}

    for param_name, param in sig.parameters.items():
        param_type = (
            param.annotation if param.annotation != inspect.Parameter.empty else Any
        )
        default_value = (
            param.default if param.default != inspect.Parameter.empty else None
        )
        required = default_value is None and param.default == inspect.Parameter.empty

        if isinstance(param_type, type) and issubclass(param_type, BaseModel):
            nested_fields = get_pydantic_fields(param_type, parsed_docstring)

            input_parameters[param_name] = Param(
                name=param_name,
                description=next(
                    (
                        "" if p.description is None else p.description
                        for p in parsed_docstring.params
                        if p.arg_name == param_name
                    ),
                    "",
                )
                if parsed_docstring
                else "",
                data_type="object",
                default_value=default_value,
                required=required,
                nested_fields=nested_fields,
            )
        else:
            input_parameters[param_name] = Param(
                name=param_name,
                description=next(
                    (
                        "" if p.description is None else p.description
                        for p in parsed_docstring.params
                        if p.arg_name == param_name
                    ),
                    "",
                )
                if parsed_docstring
                else "",
                data_type=json_datatype_from_python_type(param_type),
                default_value=default_value,
                required=required,
            )

    return input_parameters


def get_output_parameters(
    func: Callable, parsed_docstring: Optional[Docstring]
) -> List[Param]:
    signature = inspect.signature(func)
    return_annotation = signature.return_annotation
    return_description = (
        parsed_docstring.returns.description
        if parsed_docstring and parsed_docstring.returns
        else ""
    )

    if isinstance(return_annotation, type) and issubclass(return_annotation, BaseModel):
        nested_fields = get_pydantic_fields(
            return_annotation, parsed_docstring, is_output=True
        )
        return [
            Param(
                name="return_value",
                description=return_description,
                data_type="object",
                required=False,  # output is always considered optional
                nested_fields=nested_fields,
            )
        ]
    else:
        return [
            Param(
                name="return_value",
                description=return_description,
                data_type=json_datatype_from_python_type(return_annotation),
                required=False,  # output is always considered optional
            )
        ]


def get_function_metadata(func: Callable) -> FunctionMetadata:
    """
    Get metadata for a function.
    """
    # Get function name
    name = func.__name__

    # Parse docstring
    docstring = inspect.getdoc(func)
    parsed_docstring = parse(docstring) if docstring else None

    # Get description
    description: str = ""
    if parsed_docstring and parsed_docstring.short_description is not None:
        description = parsed_docstring.short_description

    # Get input and output parameters
    input_parameters = get_input_parameters(func, parsed_docstring)
    output_parameters = get_output_parameters(func, parsed_docstring)

    return FunctionMetadata(
        name=name,
        description=description,
        input_parameters=input_parameters,
        output_parameters=output_parameters,
        doc_string=docstring or "",
    )


def convert_json_to_args(func: callable, json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON data to function arguments based on function signature and type hints.

    Args:
        func (callable): The function to convert arguments for.
        json_data (Dict[str, Any]): The JSON data to convert.

    Returns:
        Dict[str, Any]: A dictionary of converted arguments.

    Raises:
        ValueError: If the JSON data is invalid or doesn't match the function signature.
    """
    signature = inspect.signature(func)
    converted_args = {}

    for param_name, param in signature.parameters.items():
        if param_name not in json_data:
            if param.default is inspect.Parameter.empty:
                raise ValueError(f"Missing required parameter: {param_name}")
            continue

        param_type = param.annotation
        value = json_data[param_name]

        if isinstance(param_type, type) and issubclass(param_type, BaseModel):
            try:
                converted_args[param_name] = param_type(**value)
            except ValidationError as e:
                raise ValueError(f"Invalid data for parameter {param_name}: {str(e)}")
        else:
            converted_args[param_name] = value

    return converted_args


def validate_and_call_workflow(
    workflow_func: Callable, json_data: Dict[str, Any]
) -> Any:
    """
    Validate the JSON data against the workflow function's metadata and call the function.

    Args:
        workflow_func (Callable): The workflow function to be called.
        json_data (Dict[str, Any]): The JSON data to be used as arguments.

    Returns:
        Any: The result of the workflow function.

    Raises:
        ValueError: If the JSON data is invalid or doesn't match the function signature.
    """
    # Get function metadata
    metadata: FunctionMetadata = get_function_metadata(workflow_func)

    # Validate input parameters
    for param_name, param in metadata.input_parameters.items():
        if param.required and param_name not in json_data:
            raise ValueError(f"Missing required parameter: {param_name}")

        if param_name in json_data:
            # You might want to add more specific type checking here
            if param.data_type == "object" and not isinstance(
                json_data[param_name], dict
            ):
                raise ValueError(
                    f"Invalid type for parameter {param_name}. Expected object, got {type(json_data[param_name])}"
                )
            elif param.data_type == "array" and not isinstance(
                json_data[param_name], list
            ):
                raise ValueError(
                    f"Invalid type for parameter {param_name}. Expected array, got {type(json_data[param_name])}"
                )

    # Convert JSON to function arguments
    args = convert_json_to_args(workflow_func, json_data)

    # Call the workflow function
    result = workflow_func(**args)

    return result
