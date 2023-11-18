from __future__ import division
from __future__ import unicode_literals
from builtins import range
__docformat__ = 'restructuredtext'

from scipy.sparse.linalg import splu

from fipy.solvers.scipy.scipySolver import ScipySolver
from fipy.tools import numerix

__all__ = ["LinearLUSolver"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class LinearLUSolver(ScipySolver):
    """
    The `LinearLUSolver` solves a linear system of equations using
    LU-factorization.  The `LinearLUSolver` is a wrapper class for the
    the Scipy `scipy.sparse.linalg.splu` module.
    """

    def _adaptLegacyTolerance(self, L, x, b):
        return self._adaptInitialTolerance(L, x, b)

    def _adaptUnscaledTolerance(self, L, x, b):
        return (1., None)

    def _adaptRHSTolerance(self, L, x, b):
        return (self._rhsNorm(L, x, b), None)

    def _adaptMatrixTolerance(self, L, x, b):
        return (self._matrixNorm(L, x, b), None)

    def _adaptInitialTolerance(self, L, x, b):
        return (self._residualNorm(L, x, b), None)

    def _solve_(self, L, x, b):
        tolerance_scale, _ = self._adaptTolerance(L, x, b)

        self._log.debug("BEGIN solve")

        LU = splu(L.matrix.asformat("csc"), diag_pivot_thresh=1.,
                                            relax=1,
                                            panel_size=10,
                                            permc_spec=3)

        for iteration in range(min(self.iterations, 10)):
            residualVector, residual = self._residualVectorAndNorm(L, x, b)

            if residual <= self.tolerance * tolerance_scale:
                break

            xError = LU.solve(residualVector)
            x[:] = x - xError

        self._log.debug("END solve")

        self._setConvergence(suite="scipy",
                             code=0,
                             iterations=iteration+1,
                             residual=residual)

        self.convergence.warn()

        return x
