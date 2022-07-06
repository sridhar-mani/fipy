from __future__ import unicode_literals
__docformat__ = 'restructuredtext'

from PyTrilinos import AztecOO

_reason = {AztecOO.AZ_normal : 'AztecOO.AZ_normal',
           AztecOO.AZ_param : 'AztecOO.AZ_param',
           AztecOO.AZ_breakdown : 'AztecOO.AZ_breakdown',
           AztecOO.AZ_loss : 'AztecOO.AZ_loss',
           AztecOO.AZ_ill_cond : 'AztecOO.AZ_ill_cond',
           AztecOO.AZ_maxits : 'AztecOO.AZ_maxits'}

from .trilinosSolver import TrilinosSolver
from .preconditioners.jacobiPreconditioner import JacobiPreconditioner
from fipy.solvers import (NormalConvergence,
                          ParameterWarning,
                          BreakdownWarning,
                          LossOfPrecisionWarning,
                          MatrixIllConditionedWarning,
                          MaximumIterationWarning)

__all__ = ["TrilinosAztecOOSolver"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class TrilinosAztecOOSolver(TrilinosSolver):

    """
    .. attention:: This class is abstract, always create on of its subclasses.
       It provides the code to call all solvers from the Trilinos AztecOO package.

    """

    AZ_r0 = AztecOO.AZ_r0
    AZ_rhs = AztecOO.AZ_rhs
    AZ_Anorm = AztecOO.AZ_Anorm
    AZ_noscaled = AztecOO.AZ_noscaled
    AZ_sol = AztecOO.AZ_sol

    @property
    def convergenceCheck(self):
        """Residual expression to compare to `tolerance`.

        (see https://trilinos.org/oldsite/packages/aztecoo/AztecOOUserGuide.pdf)
        """
        return self._convergenceCheck

    @convergenceCheck.setter
    def convergenceCheck(self, value):
        self._convergenceCheck = value

    def __init__(self, tolerance=1e-10, iterations=1000, precon=JacobiPreconditioner()):
        """
        Parameters
        ----------
        tolerance : float
            Required error tolerance.
        iterations : int
            Maximum number of iterative steps to perform.
        precon : ~fipy.solvers.trilinos.preconditioners.preconditioner.Preconditioner
        """
        if self.__class__ is TrilinosAztecOOSolver:
            raise NotImplementedError("can't instantiate abstract base class")

        TrilinosSolver.__init__(self, tolerance=tolerance,
                                iterations=iterations, precon=None)
        self.preconditioner = precon
        self._convergenceCheck = None

    def _solve_(self, L, x, b):

        Solver = AztecOO.AztecOO(L, x, b)
        Solver.SetAztecOption(AztecOO.AZ_solver, self.solver)

##        Solver.SetAztecOption(AztecOO.AZ_kspace, 30)

        Solver.SetAztecOption(AztecOO.AZ_output, AztecOO.AZ_none)

        if self.convergenceCheck is not None:
            Solver.SetAztecOption(AztecOO.AZ_conv, self.convergenceCheck)

        if self.preconditioner is not None:
            self.preconditioner._applyToSolver(solver=Solver, matrix=L)
        else:
            Solver.SetAztecOption(AztecOO.AZ_precond, AztecOO.AZ_none)

        output = Solver.Iterate(self.iterations, self.tolerance)

        if self.preconditioner is not None:
            if hasattr(self.preconditioner, 'Prec'):
                del self.preconditioner.Prec

        status = Solver.GetAztecStatus()

        # normalize across solver packages
        self.status['iterations'] = status[AztecOO.AZ_its]
        self.status['residual'] = status[AztecOO.AZ_r]
        self.status['scaled residual'] = status[AztecOO.AZ_scaled_r]
        self.status['convergence residual'] = status[AztecOO.AZ_rec_r]
        self.status['solve time'] = status[AztecOO.AZ_solve_time]
        self.status['Aztec version'] = status[AztecOO.AZ_Aztec_version]
        self.status['result'] = self._warningDict[status[AztecOO.AZ_why]].__class__.__name__

        self._raiseWarning(status[AztecOO.AZ_why],
                           status[AztecOO.AZ_its],
                           status[AztecOO.AZ_scaled_r])

        self._log.debug('iterations: %d / %d', status[AztecOO.AZ_its], self.iterations)
        self._log.debug('failure: %s', _reason[status[AztecOO.AZ_why]])
        self._log.debug('AztecOO.AZ_r: %s', status[AztecOO.AZ_r])
        self._log.debug('AztecOO.AZ_scaled_r: %s', status[AztecOO.AZ_scaled_r])
        self._log.debug('AztecOO.AZ_solve_time: %s', status[AztecOO.AZ_solve_time])
        self._log.debug('AztecOO.AZ_Aztec_version: %s', status[AztecOO.AZ_Aztec_version])

        return output

    _warningDict = {AztecOO.AZ_normal : NormalConvergence,
                    AztecOO.AZ_param : ParameterWarning,
                    AztecOO.AZ_breakdown : BreakdownWarning,
                    AztecOO.AZ_loss : LossOfPrecisionWarning,
                    AztecOO.AZ_ill_cond : MatrixIllConditionedWarning,
                    AztecOO.AZ_maxits : MaximumIterationWarning}

    def _raiseWarning(self, info, iter, relres):
        if info != AztecOO.AZ_normal:
            # is stacklevel=5 always what's needed to get to the user's scope?
            import warnings
            warnings.warn(self._warningDict[info](self, iter, relres), stacklevel=5)
