from typing import Generator

import mongomock
import pytest
from fastapi.testclient import TestClient

from cs_insights_prediction_endpoint import __version__
from cs_insights_prediction_endpoint.app import app
from cs_insights_prediction_endpoint.models.generic_model import generic_input_model
from cs_insights_prediction_endpoint.routes.route_model import (
    model_creation_request,
    model_deletion_request,
    model_function_request,
    model_update_request,
)
from cs_insights_prediction_endpoint.utils.storage_controller import (
    get_storage_controller,
)


@pytest.fixture()
def client() -> Generator:
    """Get the test client for tests and reuse it.

    Yields:
        Generator: Yields the test client as input argument for each test.
    """
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def endpoint() -> str:
    """Get the endpoint for tests.

    Returns:
        str: The endpoint including current version.
    """
    return f"/api/v{__version__.split('.')[0]}/models/"


@pytest.fixture
def i_modelCreationRequest() -> model_creation_request:
    """Get a correct model creation request

    Returns:
        ModelCreationRequest: An correct modelcreation request
    """
    return model_creation_request(model_type="lda", model_specification={"created_by": "Test"})


# TODO-AT change accordingly to changes in route_model.py
@pytest.fixture
def modelFunctionRequest() -> model_function_request:
    """Get a correct model deletion request

    Returns:
        ModelFunctionRequest: An correct modeldeletion request
    """
    return model_function_request(
        model_id="1234", model_type="lda", model_specification={"created_by": "Test"}
    )


# TODO-AT change accordingly to changes in route_model.py
@pytest.fixture
def modelDeletionRequest() -> model_deletion_request:
    """Get a correct model deletion request

    Returns:
        ModelDeletionRequest: An correct modeldeletion request
    """
    return model_deletion_request(
        model_id="1234", model_type="lda", model_specification={"created_by": "Test"}
    )


# TODO-AT change accordingly to changes in route_model.py
@pytest.fixture
def modelUpdateRequest() -> model_update_request:
    """Get a correct model deletion request

    Returns:
        model_update_request: An correct modeldeletion request
    """
    return model_update_request(
        model_id="1234", model_type="lda", model_specification={"created_by": "Test"}
    )


@pytest.fixture
def failing_model_creation_request() -> model_creation_request:
    """Get a failing model creation request

    Returns:
        model_creation_request: A failing modelcreation request
    """
    return model_creation_request(
        model_type="Does not exist", model_specification={"created_by": "Test"}
    )


@pytest.fixture
def modelFunctionCallRequest() -> generic_input_model:
    """Get a correct GenericInput model used for testing the function call endpoint

    Returns:
        generic_input_model: A GenericModelInput with a function call and empty data
    """
    return generic_input_model(function_call="get_topics", input_data={})


@pytest.fixture
def modelFailingFunctionCallRequest() -> generic_input_model:
    """Get an incorrect GenericInput model used for testing the function call endpoint

    Returns:
        generic_input_model: A GenericModelInput with a function call and empty data
    """
    return generic_input_model(function_call="NonExistent", input_data={})


@mongomock.patch(servers=(("127.0.0.1", 27017),))
def test_model_create(
    client: Generator, endpoint: str, i_modelCreationRequest: model_creation_request
) -> None:
    """Test for successfull model creation

    Arguments:
        client (TestClient): The current test client
        endpoint (str): Endpoint to query
        i_modelCreationRequest (ModelCreationRequest): A correct ModelCreationRequest
    """
    before_response_json = client.get(endpoint).json()
    response = client.post(endpoint, json=i_modelCreationRequest.dict())
    assert response.status_code == 201
    created_model_id = response.json()["model_id"]
    assert "location" in response.headers
    assert response.headers["location"] == endpoint + created_model_id
    response2 = client.get(endpoint)
    assert response2.status_code == 200
    response2_json = response2.json()
    assert "models" in response2_json
    assert "models" in before_response_json
    # assert response2_json["models"] == before_response_json["models"] + [created_model_id]


@mongomock.patch(servers=(("127.0.0.1", 27017),))
def test_model_list_functionCalls(client: Generator, endpoint: str) -> None:
    """Test for listing all functions of a model

    Arguments:
        client (TestClient): The current test client
        endpoint (str): Endpoint to query
    """
    models = client.get(endpoint).json()
    assert "models" in models
    test_model_id = models["models"][0]
    response = client.get(endpoint + test_model_id)
    assert response.status_code == 200
    response_json = response.json()
    assert "function_calls" in response_json
    assert len(response_json["function_calls"]) == len(
        get_storage_controller().get_model(test_model_id).function_calls
    )
    failing_response = client.get(endpoint + "thisWillNeverEverExist")
    assert failing_response.status_code == 404


@mongomock.patch(servers=(("127.0.0.1", 27017),))
def test_model_list_implemented(client: Generator, endpoint: str) -> None:
    """Test for listing implemented models

    Arguments:
        client (TestClient): The current test client
        endpoint (str): Endpoint to query
    """
    response = client.get(endpoint + "implemented")
    assert response.status_code == 200
    response_json = response.json()
    assert "models" in response_json
    assert "lda" in response_json["models"]


@mongomock.patch(servers=(("127.0.0.1", 27017),))
def test_model_create_fail(
    client: Generator, endpoint: str, failing_model_creation_request: model_creation_request
) -> None:
    """Test for failing model creation

    Arguments:
        client (TestClient): The current test client
        endpoint (str): Endpoint to query
        failing_model_creation_request (ModelCreationRequest): An incorrect ModelCreationRequest
    """
    response = client.post(endpoint, json=failing_model_creation_request.dict())
    assert response.status_code == 404


# TODO
# def test_model_update(
#     client: Generator, endpoint: str, modelUpdateRequest: ModelUpdateRequest
# ) -> None:
#     """Test for successfull model update
#
#     Arguments:
#         client (TestClient): The current test client
#         endpoint (str): Endpoint to query
#         modelUpdateRequest (ModelUpdateRequest): A correct ModelUpdateRequest
#     """
#     response = client.patch(endpoint, json=modelUpdateRequest.dict())
#     assert response.status_code == 201
#     updatedModelID = response.json()["modelID"]
#     assert updatedModelID == modelUpdateRequest.modelID
#     assert "modelID" in response.headers


@mongomock.patch(servers=(("127.0.0.1", 27017),))
def test_model_function(
    client: Generator, endpoint: str, modelFunctionCallRequest: generic_input_model
) -> None:
    """Test for successfull model update

    Arguments:
        client (TestClient): The current test client
        endpoint (str): Endpoint to query
        modelFunctionCallRequest (GenericInputModel): A GenericInput model holding the
                                                      function call as well as no data
    """
    models = client.get(endpoint).json()
    assert "models" in models
    test_model_id = models["models"][0]
    mfr = model_function_request(model_id=test_model_id)
    print(modelFunctionCallRequest.dict())
    response = client.post(endpoint + str(mfr.model_id), json=modelFunctionCallRequest.dict())
    assert response.status_code == 200
    response_json = response.json()
    assert "output_data" in response_json and "get_topics" in response_json["output_data"]


def test_failing_model_function(
    client: Generator, endpoint: str, modelFailingFunctionCallRequest: generic_input_model
) -> None:
    failing_response = client.post(
        endpoint + "nonExistentModel", json=modelFailingFunctionCallRequest.dict()
    )
    models = client.get(endpoint).json()
    assert "models" in models
    test_model_id = models["models"][0]
    mfr = model_function_request(model_id=test_model_id)
    assert failing_response.status_code == 404
    failing_response = client.post(
        endpoint + str(mfr.model_id), json=modelFailingFunctionCallRequest.dict()
    )
    assert failing_response.status_code == 404


@mongomock.patch(servers=(("127.0.0.1", 27017),))
def test_model_delete(
    client: Generator, endpoint: str, modelDeletionRequest: model_deletion_request
) -> None:
    """Test for successfull model deletion

    Arguments:
        client (TestClient): The current test client
        endpoint (str): Endpoint to query
        modelDeletionRequest (ModelDeletionRequest): A correct ModelDeletionRequest
    """
    models = client.get(endpoint).json()
    assert "models" in models
    test_model_id = models["models"][0]
    mdr = model_deletion_request(model_id=test_model_id)
    response = client.delete(endpoint + str(mdr.model_id))
    assert response.status_code == 200
    deletedModelID = response.json()["model_id"]
    assert deletedModelID == mdr.model_id
    failing_response = client.delete(endpoint + "thisWillNeverEverExist")
    assert failing_response.status_code == 404
