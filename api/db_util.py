import requests
from typing import Dict, Any, Optional
from utility_services import get_url, authenticate
from flask import current_app


def create_or_update_pocketbase_collection(
    collection_name: str,
    schema: Dict[str, Any],
    collection_type: str = 'base',
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    """
    Create a PocketBase collection if it doesn't exist, otherwise update it.

    Args:
        collection_name (str): Name of the collection to create or update.
        schema (Dict[str, Any]): Schema for the collection.
        collection_type (str, optional): Type of the collection. Defaults to 'base'.
        **kwargs (Any): Additional fields to include in the collection data.

    Returns:
        Optional[Dict[str, Any]]: The response JSON from the PocketBase API, or None if an error occurred.
    """
    url: str = f"{get_url()}/api/collections"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": authenticate()
    }
    data: Dict[str, Any] = {
        "name": collection_name,
        "type": collection_type,
        "schema": schema
    }
    # Include any additional fields
    data.update(kwargs)
    
    # Get the list of collections
    response: requests.Response = requests.get(url, headers=headers)
    if response.status_code == 200:
        collections: Any = response.json()["items"]
        collection: Optional[Dict[str, Any]] = next(
            (col for col in collections if col["name"] == collection_name), None)
        if collection:
            # If the collection already exists, get the id and update it
            collection_id: str = collection['id']
            response = requests.patch(
                f"{url}/{collection_id}", json=data, headers=headers)
        else:
            # Otherwise, create the collection
            current_app.logger.info(
                f"Creating or updating collection: {collection_name}")
            response = requests.post(url, json=data, headers=headers)
            print("Response data:", response.json())
    else:
        print("Response data:", response.json())
        return None

    return response.json()
