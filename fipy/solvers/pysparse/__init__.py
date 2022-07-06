from __future__ import unicode_literals

import logging

_log = logging.getLogger(__name__)

from .linearCGSSolver import *
from .linearPCGSolver import *
from .linearGMRESSolver import *
from .linearLUSolver import *
from .linearJORSolver import *

from .preconditioners import *

from . import pysparseConvergence

DefaultSolver = LinearPCGSolver
DefaultAsymmetricSolver = LinearLUSolver
DummySolver = DefaultSolver
GeneralSolver =  LinearLUSolver

__all__ = ["DefaultSolver",
           "DummySolver",
           "DefaultAsymmetricSolver",
           "GeneralSolver"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

__all__.extend(linearCGSSolver.__all__)
__all__.extend(linearPCGSolver.__all__)
__all__.extend(linearGMRESSolver.__all__)
__all__.extend(linearLUSolver.__all__)
__all__.extend(linearJORSolver.__all__)
__all__.extend(preconditioners.__all__)
