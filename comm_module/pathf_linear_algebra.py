import math as m
from numpy import array as np_vector
from numpy import dot as dot_product
from numpy import clip as clip
from numpy import arccos as arccos
from numpy import sqrt as sqrt


def normalize_angle(theta):
    """Normalize angle to be within [0, 2π)."""
    while theta < 0:
        theta += 2 * m.pi
    while theta >= 2 * m.pi:
        theta -= 2 * m.pi
    return theta


def vector_from_to(pointA: tuple, pointB: tuple) -> np_vector:
    """Create a vector from pointA to pointB."""
    return np_vector([pointB[0] - pointA[0], pointB[1] - pointA[1]])


def magnitude(vector: np_vector) -> float:
    """Calculate the magnitude (length) of a vector."""
    return sqrt(vector[0] ** 2 + vector[1] ** 2)


def angle_between_vectors(vector_a: np_vector, vector_b: np_vector):
    """Calculate the angle (in radians) between two vectors."""

    # Dot product of the vectors
    dot_product_var = dot_product(vector_a, vector_b)

    # Magnitudes of the vectors
    magnitude_a = magnitude(vector_a)
    magnitude_b = magnitude(vector_b)

    # Cosine of the angle
    cos_theta = dot_product_var / (magnitude_a * magnitude_b)

    # Clip cos_theta to avoid numerical issues outside the range [-1, 1]
    cos_theta = clip(cos_theta, -1.0, 1.0)

    # Angle in radians
    angle_radians = arccos(cos_theta)

    return angle_radians


def normal(vector: np_vector, clockwise=False):
    """Calculate the normal vector of a given vector in two dimensions."""

    # Control the orientation of the normal vector manually if need be.
    if clockwise:
        normal_vector = np_vector([vector[1], -vector[0]])
    else:
        normal_vector = np_vector([-vector[1], vector[0]])

    return normal_vector


def normalize(vector: np_vector):
    """Normalize a vector to length 1."""

    return vector / magnitude(vector)


def basis_transform_2d(
    input_vector: np_vector, basis_vector1: np_vector, basis_vector2: np_vector
):
    """Transform a vector to a new basis in two dimensions."""

    transformed_vector_x = (
        input_vector[0] * basis_vector1[0] + input_vector[1] * basis_vector2[0]
    )
    transformed_vector_y = (
        input_vector[0] * basis_vector1[1] + input_vector[1] * basis_vector2[1]
    )

    return np_vector([transformed_vector_x, transformed_vector_y])


def orthogonal_projection(projected: np_vector, projected_on: np_vector):
    """Project a vector upon another vector."""

    dot_product_var = dot_product(projected, projected_on)

    scaling = dot_product_var / (magnitude(projected_on) ** 2)

    return scaling * projected_on


def correct_direction(projection: np_vector, direction: np_vector):
    """Check the quotient between two parallel vectors and use it to check if they point in the same direction or not."""

    # Avoid division by zero.
    if projection[0] != 0 and direction[0] != 0:
        quotient = projection[0] / direction[0]
    elif projection[1] != 0 and direction[1] != 0:
        quotient = projection[1] / direction[1]
    else:
        return False

    return quotient > 0
