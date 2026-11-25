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


def orbit_directions(r, v, frame="J2000"):
    """Unit vectors for prograde, retrograde, normal and anti-normal.

    Parameters
    ----------
    r, v : array_like
        Position and velocity vectors in J2000.
    frame : str
        ``"J2000"`` returns the vectors in J2000. ``"LVLH"`` returns them in
        the local-vertical/local-horizontal frame (see :func:`lvlh_matrix`).

    Returns
    -------
    dict
        Keys ``prograde``, ``retrograde``, ``normal``, ``anti-normal``.
    """
    if frame not in ("J2000", "LVLH"):
        raise ValueError(f"unknown frame {frame!r}; expected 'J2000' or 'LVLH'")
    r = np.asarray(r, dtype=float).ravel()
    v = np.asarray(v, dtype=float).ravel()
    vn = np.linalg.norm(v)
    if vn == 0:
        raise ValueError("zero velocity vector")
    h = np.cross(r, v)
    hn = np.linalg.norm(h)
    if hn == 0:
        raise ValueError("position and velocity are collinear")
    prograde = v / vn
    normal = h / hn
    out = {
        "prograde": prograde,
        "retrograde": -prograde,
        "normal": normal,
        "anti-normal": -normal,
    }
    if frame == "LVLH":
        M = lvlh_matrix(r, v)
        out = {name: M @ vec for name, vec in out.items()}
    return out


_BASE_SEQUENCES = ("XYX", "XYZ", "XZX", "XZY", "YXY", "YXZ", "YZX", "YZY", "ZXY", "ZXZ", "ZYX", "ZYZ")
EULER_SEQUENCES = _BASE_SEQUENCES + tuple(s.lower() for s in _BASE_SEQUENCES)


def _check_sequence(seq):
    if seq not in EULER_SEQUENCES:
        raise ValueError(f"unknown Euler sequence {seq!r}; expected one of {', '.join(EULER_SEQUENCES)}")


def euler_to_quat(angles, seq="ZYX"):
    """Convert Euler angles in degrees to a scalar-first quaternion.

    Parameters
    ----------
    angles : array_like
        Three angles in degrees, in the order given by ``seq``.
    seq : str
        Rotation sequence. Uppercase is intrinsic, lowercase is extrinsic.
        All 24 proper Euler and Tait-Bryan sequences are supported.

    Returns
    -------
    ndarray
        Quaternion [w, x, y, z].
    """
    _check_sequence(seq)
    x, y, z, w = Rotation.from_euler(seq, np.asarray(angles, dtype=float).ravel(), degrees=True).as_quat()
    return np.array([w, x, y, z])


def quat_to_euler(q, seq="ZYX"):
    """Convert a quaternion to Euler angles in degrees.

    Parameters
    ----------
    q : array_like
        Quaternion [w, x, y, z].
    seq : str
        Rotation sequence. See :func:`euler_to_quat`.

    Returns
    -------
    tuple
        Three angles in degrees, in the order given by ``seq``.
    """
    _check_sequence(seq)
    return tuple(float(a) for a in to_rotation(q).as_euler(seq, degrees=True))


def lvlh_matrix(r, v):
    """Rotation matrix from J2000 to LVLH for a position and velocity.

    LVLH axes: Z nadir (-r), Y negative orbit normal (-(r x v)), X completes
    the right-handed frame. Rows are the LVLH axes in J2000 coordinates, so
    ``lvlh_matrix(r, v) @ x_j2000`` gives the same vector in LVLH.

    Parameters
    ----------
    r, v : array_like
        Position and velocity vectors in J2000.

    Returns
    -------
    ndarray
        3x3 matrix.
    """
    r = np.asarray(r, dtype=float).ravel()
    v = np.asarray(v, dtype=float).ravel()
    h = np.cross(r, v)
    hn = np.linalg.norm(h)
    if hn == 0:
        raise ValueError("position and velocity are collinear")
    z = -r / np.linalg.norm(r)
    y = -h / hn
    x = np.cross(y, z)
    return np.vstack([x, y, z])


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
