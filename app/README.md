# Vehicle Service API — Python Implementation

A Flask server that implements the Vehicle Service API contract defined in the
**Vehicle Service Collection** Postman collection. All five CRUD endpoints are
covered and protected by API key authentication (`X-API-Key` header), matching
the SDK and collection auth configuration.

---

## Endpoints

| Method | Path | Description | Success code |
|--------|------|-------------|--------------|
| `POST` | `/vehicles` | Register a new vehicle | `201 Created` |
| `GET` | `/vehicles` | List all vehicles | `200 OK` |
| `GET` | `/vehicles/:id` | Fetch a vehicle by ID | `200 OK` |
| `PATCH` | `/vehicles/:id` | Partially update a vehicle | `200 OK` |
| `DELETE`| `/vehicles/:id` | Remove a vehicle | `204 No Content` |

---

## Prerequisites

- Python 3.9+
- pip

---

## Setup

### 1. Install dependencies

```bash
cd app
pip install -r requirements.txt
```

### 2. Set your API key

The server validates the `X-API-Key` header on every request.
Set the key as an environment variable — **never commit a raw key to this repo**.

```bash
# macOS / Linux
export API_KEY=your-secret-key

# Windows CMD
set API_KEY=your-secret-key

# Windows PowerShell
$env:API_KEY="your-secret-key"
```

> **Postman Vault tip:** Store the same value under `vault:apiKey` in Postman
> so the collection can authenticate automatically without exposing the key in
> shared environment files.

### 3. Run the server

```bash
python main.py
```

The server starts on **http://localhost:60555** by default — matching the
`baseUrl` configured in the *Local – Agent Mode* Postman environment.

Override the port with the `PORT` environment variable:

```bash
PORT=8080 python main.py
```

Enable Flask's debug/reloader mode:

```bash
FLASK_DEBUG=true python main.py
```

---

## Using the Postman Python SDK

The generated SDK (located at `postman/sdks/Collections SDKs/Vehicle Service Collection/python/`)
can be used by any client that needs to call this server programmatically.

Install the SDK:

```bash
pip install postman/sdks/Collections\ SDKs/Vehicle\ Service\ Collection/python/
```

Quick example:

```python
from vehicle_service_collection_sdk import VehicleServiceCollectionSdk
from vehicle_service_collection_sdk.models import CreateAVehicleRequest

sdk = VehicleServiceCollectionSdk(
    api_key="your-secret-key",
    base_url="http://localhost:60555",
)

# Create a vehicle
new_vehicle = sdk.vehicle_service_collection_sdk.create_a_vehicle(
    CreateAVehicleRequest(
        nick_name="The Lisa Marie",
        vin="4M2DV11W4RDJ53329",
        make="Mercury",
        model="Villager",
        year="1994",
        miles=159864,
    )
)
print(new_vehicle)

# List all vehicles
all_vehicles = sdk.vehicle_service_collection_sdk.get_all_vehicles()
print(all_vehicles)

# Retrieve a single vehicle
vehicle = sdk.vehicle_service_collection_sdk.retrieve_a_vehicle("1")
print(vehicle)
```

---

## Response codes

| Code | Meaning |
|------|---------|
| `200 OK` | Successful retrieval or update |
| `201 Created` | Vehicle successfully created |
| `204 No Content` | Vehicle successfully deleted |
| `400 Bad Request` | Missing or invalid request attribute |
| `401 Unauthorized` | Missing or invalid `X-API-Key` |
| `404 Not Found` | Vehicle ID does not exist |
| `409 Conflict` | A vehicle with the same VIN already exists |
| `500 Internal Server Error` | Unexpected server-side failure |

---

## Data storage

The server uses **in-memory storage** — data is lost when the server restarts.
This is intentional for local development and Postman collection testing.
