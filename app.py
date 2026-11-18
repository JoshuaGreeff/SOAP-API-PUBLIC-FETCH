"""A small Flask wrapper around a public SOAP service for Module 5."""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, request
from zeep import Client, helpers
from zeep.exceptions import Error as ZeepError


app = Flask(__name__)

# This public WSDL comes from the instructor-provided SOAP service list.
WSDL_URL = "https://www.crcind.com/csp/samples/SOAP.Demo.cls?WSDL=1"
MINIMUM_NUMBER = -10_000
MAXIMUM_NUMBER = 10_000


class InputValidationError(ValueError):
    """Raised when a caller supplies an input outside this small demo's rules."""


def validate_integer(value: Any, field_name: str) -> int:
    """Convert one request value to an allowed whole number."""
    # JSON and query strings can both arrive as text, so convert them first.
    if isinstance(value, bool):
        raise InputValidationError(
            f"{field_name} must be a whole number between "
            f"{MINIMUM_NUMBER} and {MAXIMUM_NUMBER}."
        )

    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        # This custom message is concatenated with the original conversion error.
        raise InputValidationError(
            f"Invalid {field_name}. Enter a whole number between "
            f"{MINIMUM_NUMBER} and {MAXIMUM_NUMBER}. Details: {exc}"
        ) from exc

    if not MINIMUM_NUMBER <= number <= MAXIMUM_NUMBER:
        raise InputValidationError(
            f"Invalid {field_name}. {field_name} must be between "
            f"{MINIMUM_NUMBER} and {MAXIMUM_NUMBER}; received {number}."
        )

    return number


def validate_soap_result(value: Any) -> int:
    """Check that the SOAP result is the integer value this operation promises."""
    # AddInteger is defined in the WSDL to return xsd:long. Checking the returned
    # value demonstrates validation of data coming back from the public service.
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuntimeError(
            "SOAP response validation failed. AddIntegerResult must be a whole number. "
            f"Received: {value!r}"
        )

    minimum_result = MINIMUM_NUMBER * 2
    maximum_result = MAXIMUM_NUMBER * 2
    if not minimum_result <= value <= maximum_result:
        raise RuntimeError(
            "SOAP response validation failed. AddIntegerResult is outside the "
            f"expected range {minimum_result} through {maximum_result}. Received: {value}"
        )

    return value


def add_with_soap(arg1: Any, arg2: Any, soap_client: Client | None = None) -> dict[str, Any]:
    """Validate two values, call the public AddInteger operation, and return JSON-ready data."""
    first_number = validate_integer(arg1, "arg1")
    second_number = validate_integer(arg2, "arg2")

    try:
        # Zeep reads the WSDL and creates the AddInteger method from that contract.
        client = soap_client or Client(wsdl=WSDL_URL)
        soap_result = client.service.AddInteger(Arg1=first_number, Arg2=second_number)

        # Zeep can return XML-backed objects. This helper turns them into normal
        # Python values so Flask can safely serialize the response as JSON.
        native_result = helpers.serialize_object(soap_result)
    except ZeepError as exc:
        # Keep the custom explanation and the original SOAP/transport error together.
        raise RuntimeError(f"SOAP AddInteger request failed. Service details: {exc}") from exc
    except Exception as exc:
        # The same custom-plus-original-error pattern helps if the public service is down.
        raise RuntimeError(f"Unexpected SOAP client error. Service details: {exc}") from exc

    checked_result = validate_soap_result(native_result)

    return {
        "operation": "AddInteger",
        "inputs": {"arg1": first_number, "arg2": second_number},
        "result": checked_result,
    }


@app.get("/")
def home() -> tuple[dict[str, str], int]:
    """Give a browser or curl user the two routes to try."""
    return {
        "message": "SOAP Flask service is running.",
        "get_example": "/add?arg1=7&arg2=35",
        "post_example": "POST JSON to /add with arg1 and arg2.",
    }, 200


@app.get("/add")
def add_get() -> tuple[Any, int]:
    """Use query-string values so the SOAP operation can be tested with GET."""
    try:
        result = add_with_soap(request.args.get("arg1"), request.args.get("arg2"))
        return jsonify(result), 200
    except InputValidationError as exc:
        return jsonify({"error": f"Validation error: {exc}"}), 400
    except RuntimeError as exc:
        return jsonify({"error": f"Custom SOAP error: {exc}"}), 502


@app.post("/add")
def add_post() -> tuple[Any, int]:
    """Accept a JSON object and send its validated values to the same SOAP operation."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Validation error: Send a JSON object with arg1 and arg2."}), 400

    try:
        result = add_with_soap(payload.get("arg1"), payload.get("arg2"))
        return jsonify(result), 200
    except InputValidationError as exc:
        return jsonify({"error": f"Validation error: {exc}"}), 400
    except RuntimeError as exc:
        return jsonify({"error": f"Custom SOAP error: {exc}"}), 502


if __name__ == "__main__":
    app.run(debug=True)
