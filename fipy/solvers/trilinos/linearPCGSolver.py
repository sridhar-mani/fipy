from __future__ import unicode_literals
__docformat__ = 'restructuredtext'

from PyTrilinos import AztecOO

from fipy.solvers.trilinos.trilinosAztecOOSolver import TrilinosAztecOOSolver
from fipy.solvers.trilinos.preconditioners.multilevelDDPreconditioner import MultilevelDDPreconditioner

__all__ = ["LinearPCGSolver"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class LinearPCGSolver(TrilinosAztecOOSolver):

    """
    The `LinearPCGSolver` is an interface to the cg solver in Trilinos, using
    the `MultilevelSGSPreconditioner` by default.

    """

    def __init__(self, tolerance=1e-5, criterion="default",
                 iterations=1000, precon=MultilevelDDPreconditioner()):
        """
        Parameters
        ----------
        tolerance : float
            Required error tolerance.
        criterion : {'default', 'initial', 'unscaled', 'RHS', 'matrix', 'solution', 'legacy'}
            Interpretation of ``tolerance``.
            See :ref:`CONVERGENCE` for more information.
        iterations : int
            Maximum number of iterative steps to perform.
        precon : ~fipy.solvers.trilinos.preconditioners.preconditioner.Preconditioner
        """
        super(LinearPCGSolver, self).__init__(tolerance=tolerance, criterion=criterion,
                                              iterations=iterations, precon=precon)
        self.solver = AztecOO.AZ_cg

    def _canSolveAsymmetric(self):
        return False
