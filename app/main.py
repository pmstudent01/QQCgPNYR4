"""
Vehicle Service API
-------------------
A Flask implementation of the Vehicle Service API contract defined in the
Postman collection. Exposes 5 CRUD endpoints for the /vehicles resource,
protected by an API key supplied via the X-API-Key header.

Authentication
--------------
Set the API_KEY environment variable before starting the server:
    export API_KEY=your-secret-key          # macOS / Linux
    set API_KEY=your-secret-key             # Windows CMD
    $env:API_KEY="your-secret-key"          # Windows PowerShell

The same value must be set in your Postman Vault (vault:apiKey) or in
the active environment so that collection requests can authenticate.

Running
-------
    pip install -r requirements.txt
    python main.py

The server starts on http://localhost:60555 by default.
Override with the PORT environment variable:
    PORT=8080 python main.py
"""

import os
from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory data store
# ---------------------------------------------------------------------------
_vehicles: dict[int, dict] = {}
_next_id: int = 1

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
_API_KEY: str = os.environ.get("API_KEY", "")


def require_api_key(f):
    """Decorator that enforces X-API-Key header authentication."""

    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if not _API_KEY:
            # Server is misconfigured — reject all requests until a key is set.
            return (
                jsonify({"error": "Server API key is not configured. Set the API_KEY environment variable."}),
                500,
            )
        if key != _API_KEY:
            return jsonify({"error": "Unauthorized: invalid or missing API key"}), 401
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
_REQUIRED_FIELDS = ("nickName", "vin", "make", "model", "year", "miles")


def _build_vehicle(data: dict, vehicle_id: int) -> dict:
    return {
        "id": vehicle_id,
        "nickName": data["nickName"],
        "vin": data["vin"],
        "make": data["make"],
        "model": data["model"],
        "year": data["year"],
        "miles": data["miles"],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/vehicles", methods=["POST"])
@require_api_key
def create_vehicle():
    """POST /vehicles — register a new vehicle.

    Returns 201 Created on success.
    Returns 400 if required fields are missing.
    Returns 409 if a vehicle with the same VIN already exists.
    """
    global _next_id

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing = [f for f in _REQUIRED_FIELDS if f not in data]
    if missing:
        return (
            jsonify({"error": f"Missing required attribute(s): {', '.join(missing)}"}),
            400,
        )

    # Duplicate VIN check
    for existing in _vehicles.values():
        if existing["vin"] == data["vin"]:
            return (
                jsonify({"error": "A vehicle with this VIN already exists"}),
                409,
            )

    vehicle = _build_vehicle(data, _next_id)
    _vehicles[_next_id] = vehicle
    _next_id += 1

    return jsonify(vehicle), 201


@app.route("/vehicles", methods=["GET"])
@require_api_key
def get_all_vehicles():
    """GET /vehicles — list all vehicles.

    Returns 200 OK with an array of vehicle objects.
    """
    return jsonify(list(_vehicles.values())), 200


@app.route("/vehicles/<int:vehicle_id>", methods=["GET"])
@require_api_key
def retrieve_vehicle(vehicle_id: int):
    """GET /vehicles/:id — fetch a single vehicle by ID.

    Returns 200 OK with the vehicle object.
    Returns 404 if the ID does not exist.
    """
    vehicle = _vehicles.get(vehicle_id)
    if vehicle is None:
        return jsonify({"error": f"Vehicle {vehicle_id} not found"}), 404
    return jsonify(vehicle), 200


@app.route("/vehicles/<int:vehicle_id>", methods=["PATCH"])
@require_api_key
def update_vehicle(vehicle_id: int):
    """PATCH /vehicles/:id — partially update a vehicle.

    Returns 200 OK with the updated vehicle object.
    Returns 400 if the request body is invalid.
    Returns 404 if the ID does not exist.
    """
    vehicle = _vehicles.get(vehicle_id)
    if vehicle is None:
        return jsonify({"error": f"Vehicle {vehicle_id} not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    for field in _REQUIRED_FIELDS:
        if field in data:
            vehicle[field] = data[field]

    _vehicles[vehicle_id] = vehicle
    return jsonify(vehicle), 200


@app.route("/vehicles/<int:vehicle_id>", methods=["DELETE"])
@require_api_key
def delete_vehicle(vehicle_id: int):
    """DELETE /vehicles/:id — remove a vehicle.

    Returns 204 No Content on success.
    Returns 404 if the ID does not exist.
    """
    if vehicle_id not in _vehicles:
        return jsonify({"error": f"Vehicle {vehicle_id} not found"}), 404

    del _vehicles[vehicle_id]
    return "", 204


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Unexpected server error"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 60555))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"Starting Vehicle Service API on http://localhost:{port}")
    print(f"API key auth: {'configured' if _API_KEY else 'NOT SET — set the API_KEY env var'}")
    app.run(host="0.0.0.0", port=port, debug=debug)
