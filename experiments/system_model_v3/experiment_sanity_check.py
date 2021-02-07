import numpy as np


subset = True
if subset:
    control_period = np.linspace(1 * 3600, 6 * 3600, 2) # Default: 3 hours
    kp = np.linspace(1e-10, 1e-4, 2) # Default: 1e-8
    ki = np.linspace(-1e-10, -1e-4, 2) # Default: -1e-10
    sweeps = {
        'control_period': control_period,
        'kp': kp,
        'ki': ki,
    }
else:
    control_period = np.linspace(1 * 3600, 6 * 3600, 3) # Default: 3 hours
    kp = np.linspace(1e-10, 1e-4, 3) # Default: 1e-8
    ki = np.linspace(-1e-10, -1e-4, 3) # Default: -1e-10
    alpha = np.linspace(
        999998857063901981428416512,
        1000000000000000000000000000, # Disabled
        3
    )

    sweeps = {
        'control_period': control_period,
        'kp': kp,
        'ki': ki,
        # 'alpha': alpha
    }
