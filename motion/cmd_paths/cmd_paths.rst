========================
The paths module
========================

Paths is an abstraction module for construction of paths and trajectories on a 3D space with constraints.

Volumes can be defined using Pyrame's or custom functions. These volumes can then be used either to define forbidden zones or matrices.

Volumes are created using the :py:func:`init_volume_paths <cmd_paths.init_volume_paths>` function, which registers the volume in a pool and returns an *id*. Then, they can be used to define a forbidden region of space (:py:func:`add_limits_paths <cmd_paths.add_limits_paths>`) or a matrix of points (:py:func:`init_matrix_paths <cmd_paths.init_matrix_paths>`).

Both the function :py:func:`move_paths <cmd_paths.move_paths>` and :py:func:`next_matrix_paths<cmd_paths.next_matrix_paths>` will move in space by avoiding forbidden volumes. An A-star algorithm is used from one point to another on both functions.

.. warning::
    The complexity of the A-star path finding problem increases rapidly with decreasing values of the minimum steps (r1,r2,r3). Keep them to the largest value required on your experiment.

API
===

.. automodule:: cmd_paths
   :members:
   :member-order: bysource

