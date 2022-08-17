"""Tests for the generic model."""
from datetime import datetime

import pytest

from cs_insights_prediction_endpoint.models.generic_model import generic_model


@pytest.fixture
def dummy_generic_model() -> generic_model:
    """Provides an actual instance of the implementaion

    Returns:
        generic_model: the created generic_model
    """
    dummy_values = {
        "name": "Generic",
        "created_by": "Alpha Tester",
        "description": "This is a test",
        "creation_parameters": {},
        "function_calls": {},
        "type": "test",
    }
    dummy = generic_model(**dummy_values)
    return dummy


def test_generic_model_initial_values(dummy_generic_model: generic_model) -> None:
    """Test for checking if the generic_model gets created correctly

    Arguments:
        dummy_generic_model (Generic_Model): An instance of our generic_model implementation
    """
    assert dummy_generic_model.name == "Generic"
    assert str(hash(dummy_generic_model.name)) == dummy_generic_model.id
    assert dummy_generic_model.get_name() == dummy_generic_model.name
    assert dummy_generic_model.created_by == "Alpha Tester"
    assert dummy_generic_model.created_at <= datetime.timestamp(datetime.now()) + 1
    assert dummy_generic_model.created_at >= datetime.timestamp(datetime.now()) - 1
    assert dummy_generic_model.description == "This is a test"
    assert dummy_generic_model.creation_parameters == {}
    assert dummy_generic_model.function_calls == {}
    assert dummy_generic_model.get_function_calls() == []
    assert str(dummy_generic_model) == dummy_generic_model.id

    with pytest.raises(NotImplementedError):
        dummy_generic_model.train({})

    with pytest.raises(NotImplementedError):
        dummy_generic_model.predict({})

    with pytest.raises(NotImplementedError):
        dummy_generic_model.save("")

    with pytest.raises(NotImplementedError):
        dummy_generic_model.load("")
