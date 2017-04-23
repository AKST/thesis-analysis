import logging as l

from typing import Any
from typing import Union
from typing import Tuple

def get_logging_level(args: Any) -> Tuple[int, Union[None, str]]:
    l_level = args.log_level
    if hasattr(l, l_level):
        return getattr(l, l_level), None
    else:
        return l.ERROR, ("'%s' is not a valid logging level" % l_level)

def setup_logging(args: Any) -> l.Logger:
    log_lvl, err_msg = get_logging_level(args)
    l.basicConfig(level=log_lvl, format=args.log_format)
    if isinstance(err_msg, str):
        l.error("Non fatal error, but FYI; %s...", err_msg)
