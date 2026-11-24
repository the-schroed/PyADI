"""Quaternion / frame helpers. Scalar-first [w, x, y, z], Hamilton."""
import numpy as np
from scipy.spatial.transform import Rotation


def normalize(q):
    """Normalize a quaternion.

    Parameters
    ----------
    q : array_like
        Quaternion [w, x, y, z].

    Returns
    -------
    ndarray
        Unit quaternion.
    """
    q = np.asarray(q, dtype=float).ravel()
    n = np.linalg.norm(q)
    if n == 0:
        raise ValueError("zero quaternion")
    return q / n


def quat_mul(a, b):
    """Multiply two quaternions.

    Parameters
    ----------
    a, b : array_like
        Quaternions [w, x, y, z].

    Returns
    -------
    ndarray
        Product quaternion.
    """
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    w = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3]
    x = a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2]
    y = a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1]
    z = a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0]
    return np.array([w, x, y, z])


def quat_conj(q):
    """Conjugate of a quaternion.

    Parameters
    ----------
    q : array_like
        Quaternion [w, x, y, z].

    Returns
    -------
    ndarray
        Conjugate quaternion.
    """
    q = np.asarray(q, dtype=float)
    return np.array([q[0], -q[1], -q[2], -q[3]])


def body_to_lvlh(q_body_j2000, q_lvlh_j2000):
    """Convert body->J2000 and LVLH->J2000 to body->LVLH.

    Parameters
    ----------
    q_body_j2000, q_lvlh_j2000 : array_like
        Quaternions.

    Returns
    -------
    ndarray
        body->LVLH quaternion.
    """
    return quat_mul(quat_conj(q_lvlh_j2000), q_body_j2000)


def to_rotation(q):
    """Convert quaternion to scipy Rotation.

    Parameters
    ----------
    q : array_like
        Quaternion [w, x, y, z].

    Returns
    -------
    Rotation
    """
    q = normalize(q)
    return Rotation.from_quat([q[1], q[2], q[3], q[0]])


def rpy_deg(q):
    """Convert quaternion to roll, pitch, yaw (degrees).

    Parameters
    ----------
    q : array_like
        Quaternion [w, x, y, z].

    Returns
    -------
    tuple
        (roll, pitch, yaw) in degrees.
    """
    r = to_rotation(q)
    ypr = r.as_euler("ZYX", degrees=True)
    yaw, pitch, roll = ypr
    return float(roll), float(pitch), float(yaw)
