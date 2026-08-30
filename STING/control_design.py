import os
from pathlib import Path

import cvxpy as cp
import numpy as np
import polars as pl
from scipy.linalg import eigvals, solve_continuous_are

from cmaspy.partial_state_feedback import mas_output_feedback
from sting.modules.small_signal_modeling.core import SmallSignalModel

cwd = os.path.join(Path(__file__).resolve().parent)

def construct_controller(rom:SmallSignalModel):
    """Construct a controller using CMAS"""
    A_c = rom.model.A
    B_c = rom.model.B[:, 0:1] # take only p_ref

    C_c = np.zeros((5, A_c.shape[0]))
    C_c[0, 1] = 1 # w_pc
    C_c[1, 7] = 1 # i_vsc_d
    C_c[2, 8] = 1 # i_vsc_q
    C_c[3, 9] = 1 # i_bus_d
    C_c[4, 10] = 1 # i_bus_q 

    D_c = np.zeros((C_c.shape[0], B_c.shape[1]))

    Q = 10**4*np.eye(A_c.shape[0])
    R = 10**6*np.eye(B_c.shape[1])

    solve_settings = {'solver': cp.CLARABEL, 'verbose': False}

    # Solve CARE to obtain P
    P = solve_continuous_are(A_c, B_c, Q, R)

    # Use MAS output feedback
    alpha_coef = 100
    beta_coef = 0
    gamma_coef = 0
    mas_out = mas_output_feedback(A_c, [B_c], [C_c], [D_c], [Q], [R], [P], alpha_coef, beta_coef, gamma_coef, **solve_settings)

    # Print dominant eigenvalues of the closed-loop system
    eigenvalues = eigvals(mas_out.Acl_F)
    dominant_eigenvalue = eigenvalues[np.argmax(eigenvalues.real)]
    print("Dominant eigenvalues of the closed-loop system: ", dominant_eigenvalue)

    # Save closed-loop a matrix as csv file
    Acl_F = mas_out.Acl_F
    pl.DataFrame(Acl_F).write_csv(os.path.join(cwd, "outputs", "closed_loop_A.csv"))
    # Save the feedback controller
    F = mas_out.F[0]   

    return F