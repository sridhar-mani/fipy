#!/usr/bin/env python

## 
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "input.py"
 #                                    created: 12/29/03 {3:23:47 PM}
 #                                last update: 10/25/04 {5:36:17 PM} 
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 #  Description: 
 # 
 #  History
 # 
 #  modified   by  rev reason
 #  ---------- --- --- -----------
 #  2003-11-10 JEG 1.0 original
 # ###################################################################
 ##

r"""
This example is a 1D steady state diffusion test case with a diffusion
coefficient that spatially varies such that

.. raw:: latex

    $$ \frac{\partial }{\partial x} D \frac{\partial \phi}{\partial x} = 0, $$

with boundary conditions

.. raw:: latex

    $\phi = 0$ at $x = 0$ and $D \frac{\partial \phi}{\partial x} = 1$ at $x = L$.

The diffusion coefficient varies with the profile

.. raw:: latex

   $$ D = \begin{cases}
   1& \text{for $0 < x < L / 4$,} \\
   0.1& \text{for $L / 4 \le x < 3 L / 4$,} \\
   1& \text{for $3 L / 4 \le x < L$,}
   \end{cases} $$

where 

    >>> L = 1.
    
is the length of the bar.  Accurate answers to this
problem are given for any number of cells where `nCells = 4 * i + 2`
where `i` is an integer and of course for large `nCells`. 
In this example

    >>> nx = 10

We create a 1D mesh of the appropriate size

    >>> ny = 1
    >>> dx = L / nx
    >>> dy = 1.
    >>> from fipy.meshes.grid2D import Grid2D
    >>> mesh = Grid2D(dx, dy, nx, ny)

and initialize the solution variable to `valueLeft`:
    
    >>> valueLeft = 0.
    >>> from fipy.variables.cellVariable import CellVariable
    >>> var = CellVariable(
    ...     name = "solution variable",
    ...     mesh = mesh,
    ...     value = valueLeft)

   
In this example, the diffusion
coefficient is a numerical array that is passed to the diffusion equation.
The diffusion coefficient exists on the faces of the cells and thus has to
be the length of the faces.  It is created in the following way:

    >>> x = mesh.getFaceCenters()[:,0]
    >>> import Numeric
    >>> outerFaces = Numeric.logical_or(x < L / 4., x >= 3. * L / 4.)
    >>> diffCoeff = Numeric.where(outerFaces, 1., 0.1)

We seek a steady-state solution, so the `transientCoeff` of the `DiffusionEquation` 
is set to zero. For boundary conditions, we have no-flux conditions top and bottom, 
a fixed value of `valueLeft` to the left, and a fixed flux of 

    >>> fluxRight = 1.
    
to the right:

    >>> from fipy.boundaryConditions.fixedValue import FixedValue
    >>> from fipy.boundaryConditions.fixedFlux import FixedFlux
    >>> from fipy.solvers.linearPCGSolver import LinearPCGSolver
    >>> from fipy.equations.diffusionEquation import DiffusionEquation
    >>> eq = DiffusionEquation(
    ...     var,
    ...     transientCoeff = 0., 
    ...     diffusionCoeff = diffCoeff,
    ...     solver = LinearPCGSolver(
    ...         tolerance = 1.e-15, 
    ...         steps = 1000
    ...     ),
    ...     boundaryConditions=(
    ...         FixedValue(mesh.getFacesLeft(),valueLeft),
    ...         FixedFlux(mesh.getFacesRight(),fluxRight),
    ...         FixedFlux(mesh.getFacesTop(),0.),
    ...         FixedFlux(mesh.getFacesBottom(),0.)
    ...     )
    ... )

We iterate one time step to implicitly find the steady state
solution:

    >>> from fipy.iterators.iterator import Iterator
    >>> it = Iterator((eq,))
    >>> it.timestep()

A simple analytical answer can be used to test the result:
    
.. raw:: latex

   $$ \phi = \begin{cases}
   x & \text{for $0 < x < L/4$,} \\
   10 x - 9L/4 & \text{for $L/4 \le x < 3 L / 4$,} \\
   x + 18 L / 4 & \text{for $3 L / 4 \le x < L$,}
   \end{cases} $$

or

    >>> x = mesh.getCellCenters()[:,0]
    >>> values = x + 18. * L / 4.
    >>> values = Numeric.where(x < 3. * L / 4., 10 * x - 9. * L / 4., values)
    >>> values = Numeric.where(x < L / 4., x, values)
    >>> Numeric.allclose(values, var, atol = 1e-8, rtol = 1e-8)
    1
   
If the problem is run interactively, we can view the result:
   
    >>> if __name__ == '__main__':
    ...     from fipy.viewers.grid2DGistViewer import Grid2DGistViewer
    ...     viewer = Grid2DGistViewer(var, maxVal = L + 18. * L / 4.)
    ...     viewer.plot()
"""
__docformat__ = 'restructuredtext'

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    raw_input('finished')
