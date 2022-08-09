"""
Test file for `main.py`
"""
import main

import numpy as np

from hypothesis import given
from hypothesis.strategies import integers, floats
from hypothesis.extra.numpy import arrays


DEFAULT_NUMBER_OF_MANUSCRIPTS = 10
MIN_MANUSCRIPT_SCORE = 0
MAX_MANUSCRIPT_SCORE = 10


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
    number_of_manuscripts=integers(
        min_value=1, max_value=DEFAULT_NUMBER_OF_MANUSCRIPTS
    ),
)
def test_create_manuscript_property(seed, number_of_manuscripts):
    manuscripts = main.create_manuscripts(
        number_of_manuscripts=number_of_manuscripts, seed=seed
    )
    assert len(manuscripts) == number_of_manuscripts
    assert min(manuscripts) >= MIN_MANUSCRIPT_SCORE
    assert max(manuscripts) <= MAX_MANUSCRIPT_SCORE


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
)
def test_create_manuscript_expected_statistics(seed):
    """
    Confirm that the mean of the manuscripts is 5 and the std is 2.88.

    The std is calculated using known result for the variance of the uniform distribution:

        (b - a) ^ 2 / 12

    With b = 10 and a = 0.
    """
    manuscripts = main.create_manuscripts(number_of_manuscripts=500_000, seed=seed)
    assert min(manuscripts) >= MIN_MANUSCRIPT_SCORE
    assert max(manuscripts) <= MAX_MANUSCRIPT_SCORE
    assert np.isclose(np.round(np.mean(manuscripts), 1), 5)
    assert np.isclose(np.round(np.std(manuscripts), 1), 2.9)


def test_create_manuscript_example():
    manuscripts = main.create_manuscripts(number_of_manuscripts=10, seed=0)
    expected_manuscripts = np.array(
        [
            5.48813504,
            7.15189366,
            6.02763376,
            5.44883183,
            4.23654799,
            6.45894113,
            4.37587211,
            8.91773001,
            9.63662761,
            3.83441519,
        ]
    )
    np.allclose(manuscripts, expected_manuscripts)


@given(
    manuscripts=arrays(
        np.float64,
        DEFAULT_NUMBER_OF_MANUSCRIPTS,
        elements=floats(min_value=0, max_value=10),
    ),
    imprecision_error_sd=floats(min_value=0, max_value=2),
    other_error_sd=floats(min_value=0, max_value=2),
)
def test_review_manuscripts_property(manuscripts, imprecision_error_sd, other_error_sd):
    reviews = main.review_manuscripts(
        manuscripts=manuscripts,
        imprecision_error_sd=imprecision_error_sd,
        other_error_sd=other_error_sd,
    )
    assert np.min(reviews) >= MIN_MANUSCRIPT_SCORE
    assert np.max(reviews) <= MAX_MANUSCRIPT_SCORE
    assert len(reviews) == DEFAULT_NUMBER_OF_MANUSCRIPTS


def test_review_manuscript_example():
    manuscripts = main.create_manuscripts(number_of_manuscripts=10, seed=0)
    reviews = main.review_manuscripts(
        manuscripts=manuscripts, imprecision_error_sd=0.5, other_error_sd=0.25
    )
    expected_reviews = np.array(
        [
            4.92190937,
            8.04243507,
            6.62426167,
            5.32412808,
            5.02591827,
            6.26218688,
            5.13435128,
            8.76835491,
            10.0,
            3.77470701,
        ]
    )
    assert np.allclose(reviews, expected_reviews)


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
)
def test_review_manuscripts_expected_statistics(seed):
    """
    Confirm that the mean of the manuscripts is 5 and the std is 2.88.

    The std is calculated using known result for the variance of the uniform distribution:

        (b - a) ^ 2 / 12

    With b = 10 and a = 0.
    """
    manuscripts = main.create_manuscripts(number_of_manuscripts=500_000, seed=seed)
    reviews = main.review_manuscripts(
        manuscripts=manuscripts, imprecision_error_sd=0, other_error_sd=0.2
    )
    sampled_other_errors = reviews - manuscripts
    assert np.isclose(np.round(np.mean(sampled_other_errors), 1), 0)
    assert np.isclose(np.round(np.std(sampled_other_errors), 1), 0.2)

    reviews = main.review_manuscripts(
        manuscripts=manuscripts, imprecision_error_sd=0.5, other_error_sd=0
    )
    sampled_imprecision_errors = reviews - manuscripts
    assert np.isclose(np.round(np.mean(sampled_imprecision_errors), 1), 0)
    assert np.isclose(np.round(np.std(sampled_imprecision_errors), 1), 0.5)


@given(
    manuscripts=arrays(
        np.float64,
        DEFAULT_NUMBER_OF_MANUSCRIPTS,
        elements=floats(min_value=0, max_value=10),
    ),
    threshold=integers(min_value=0, max_value=10),
)
def test_is_above_threshold_property(manuscripts, threshold):
    accept = main.is_above_threshold(manuscripts=manuscripts, threshold=threshold)
    assert np.array_equal(accept, manuscripts >= threshold)


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
    number_of_reviews=integers(min_value=1, max_value=5),
    imprecision_error_sd=floats(min_value=0, max_value=1),
    other_error_sd=floats(min_value=0, max_value=1),
)
def test_get_average_review_property(
    seed, number_of_reviews, imprecision_error_sd, other_error_sd
):
    manuscripts = main.create_manuscripts(number_of_manuscripts=500_000, seed=seed)
    average_reviews = main.get_average_review_scores(
        manuscripts=manuscripts,
        number_of_reviews=number_of_reviews,
        imprecision_error_sd=imprecision_error_sd,
        other_error_sd=other_error_sd,
    )
    assert len(average_reviews) == len(manuscripts)

    sampled_errors = manuscripts - average_reviews
    assert np.isclose(np.round(np.mean(sampled_errors), 1), 0)


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
    number_of_reviews=integers(min_value=1, max_value=5),
    imprecision_error_sd=floats(min_value=0, max_value=1),
    other_error_sd=floats(min_value=0, max_value=1),
    threshold=integers(min_value=0, max_value=10),
)
def test_is_above_threshold_based_on_average(
    seed, number_of_reviews, imprecision_error_sd, other_error_sd, threshold
):
    manuscripts = main.create_manuscripts(
        number_of_manuscripts=DEFAULT_NUMBER_OF_MANUSCRIPTS, seed=seed
    )
    accept = main.is_above_threshold_based_on_average(
        manuscripts=manuscripts,
        imprecision_error_sd=imprecision_error_sd,
        other_error_sd=other_error_sd,
        threshold=threshold,
        number_of_reviews=number_of_reviews,
    )
    assert len(accept) == len(manuscripts)
    assert set(accept) <= {True, False}


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
    number_of_reviews=integers(min_value=1, max_value=5),
    imprecision_error_sd=floats(min_value=0, max_value=1),
    other_error_sd=floats(min_value=0, max_value=1),
    threshold=integers(min_value=0, max_value=10),
)
def test_is_above_threshold_based_on_vote(
    seed, number_of_reviews, imprecision_error_sd, other_error_sd, threshold
):
    manuscripts = main.create_manuscripts(
        number_of_manuscripts=DEFAULT_NUMBER_OF_MANUSCRIPTS, seed=seed
    )
    accept = main.is_above_threshold_based_on_vote(
        manuscripts=manuscripts,
        imprecision_error_sd=imprecision_error_sd,
        other_error_sd=other_error_sd,
        threshold=threshold,
        number_of_reviews=number_of_reviews,
    )
    assert len(accept) == len(manuscripts)
    assert set(accept) <= {True, False}


@given(
    seed=integers(min_value=0, max_value=2**32 - 1),
    number_of_reviews=integers(min_value=1, max_value=5),
    imprecision_error_sd=floats(min_value=0, max_value=1),
    other_error_sd=floats(min_value=0, max_value=1),
    threshold=integers(min_value=0, max_value=10),
)
def test_accuracy_of_process(
    seed, number_of_reviews, imprecision_error_sd, other_error_sd, threshold
):
    manuscripts = main.create_manuscripts(
        number_of_manuscripts=DEFAULT_NUMBER_OF_MANUSCRIPTS, seed=seed
    )
    for process in (
        main.is_above_threshold_based_on_average,
        main.is_above_threshold_based_on_vote,
    ):
        accuracy = main.accuracy_of_process(
            manuscripts=manuscripts,
            imprecision_error_sd=imprecision_error_sd,
            threshold=threshold,
            process=process,
            other_error_sd=other_error_sd,
            number_of_reviews=number_of_reviews,
        )
        assert 0 <= accuracy <= 1
