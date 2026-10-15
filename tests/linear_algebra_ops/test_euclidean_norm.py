import numpy as np
import pytest

from biomechzoo.linear_algebra_ops.euclidean_norm import euclidean_norm


def test_euclidean_norm_2d():
    result = euclidean_norm(np.array([3, 0]), np.array([4, 5]))

    np.testing.assert_allclose(result, [5, 5])


def test_euclidean_norm_3d():
    result = euclidean_norm(np.array([1]), np.array([2]), np.array([2]))

    np.testing.assert_allclose(result, [3])


def test_euclidean_norm_rejects_different_vector_lengths():
    with pytest.raises(ValueError, match="same length"):
        euclidean_norm(np.array([1, 2]), np.array([3]), np.array([4, 5]))
