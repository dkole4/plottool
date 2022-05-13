"""
This module provides utility needed in other modules of the application.

Classes:

    ExtendedEnum

Functions:

    parse_command_arguments(List[Type])
    -> Callable[[Callable[..., RT]], Callable[..., RT]]

    validate_command_arguments(List[Callable])
    -> Callable[[Callable[..., RT]], Callable[..., RT]]

    greater_or_equal(int) -> Callable[[int], bool]
"""
from enum import Enum
import functools
from typing import Any, Callable, List, Type, TypeVar


class ExtendedEnum(Enum):
    """Extended version of enum that allows requesting
    lists of values and names separately.
    """
    @classmethod
    def get_values(cls) -> List[Any]:
        """Get the list of values of enum.

        Returns:
            List[Any]: List of enum values.
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def get_names(cls) -> List[str]:
        """Get the list of names of enum.

        Returns:
            List[str]: List of enum names.
        """
        return list(map(lambda c: c.name, cls))


RT = TypeVar("RT")


def parse_command_arguments(
    *types: List[Type]
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Parse user command arguments into requested types.

    Args:
        types (List[Type]): List of types to use in argument casting.

    Returns:
        Callable[[Callable[..., RT]], Callable[..., RT]]: Decorator of
        the user command function.
    """
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> RT:
            arg_num = len(args)

            # Try to parse arguments into requested types.
            parsed = []
            for (arg, arg_type) in zip(args[:arg_num], types[:arg_num]):
                parsed.append(arg_type(arg))

            return func(self, *parsed, **kwargs)

        return wrapper
    return decorator


def validate_command_arguments(
    *checks: List[Callable]
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Validate user command arguments.

    Args:
        checks (List[Callable]): List of fuctions to use
        in argument validation.

    Returns:
        Callable[[Callable[..., RT]], Callable[..., RT]]: Decorator of
        the user command function.
    """
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        def wrapper(self, *args, **kwargs) -> RT:
            arg_num = len(args)

            # Check argument value using given functions.
            for (arg, check) in zip(args[:arg_num], checks[:arg_num]):
                if not check:
                    # Skip if current argument doesn't need validation
                    continue

                if not check(arg):
                    raise ValueError("AT LEAST ONE GIVEN VALUE IS INVALID")

            return func(self, *args, **kwargs)

        return wrapper
    return decorator


# -----------------
# Validation checks

def greater_or_equal(limit: int) -> Callable[[int], bool]:
    """Check function for validate_command_arguments fuction to determine
    whether given int argument is greater or equal to set limit.

    Args:
        limit (int): Limit to compare argument to.

    Returns:
        Callable[[int], bool]: Function that compares argument to set limit.
    """
    return lambda x: x >= limit
