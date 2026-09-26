import json

def save_layout_state(geometry_bytes, state_bytes, config_path):
    """Stores Qt binary window geometry and dock states as hex strings in JSON."""
    payload = {
        "window_geometry": geometry_bytes.toHex().data().decode("utf-8"),
        "window_state": state_bytes.toHex().data().decode("utf-8")
    }

    data = {}
    try :
        with open(config_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Read error or corrupt JSON file. Re-initializing structure. Details: {e}")

    data["layout_data"] = payload
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)

def load_layout_state(config_path):
    """Reads hex strings from JSON and returns them, or None if missing."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)["layout_data"]
    except (json.JSONDecodeError, IOError):
        return None