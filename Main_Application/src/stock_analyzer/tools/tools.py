import requests
BASE_URL="http://localhost:8000"
def get_store_stock(store_id:str)->str:
     """Fetches the stock data for a specific store by its ID."""
     res=requests.get(f"{BASE_URL}/store/{store_id}")
     return res.text
def buy_from_store(store_id:str,item_id:int,quantity:int)->str:
    """Buys a quantity of an item from the given store."""
    res = requests.post(
        f"{BASE_URL}/store/{store_id}/buy",
        json={"item_id": item_id, "quantity": quantity}
    )
    return res.text
def update_inventory(store_id: str, item_id: int, item_name: str, quantity: int, price: float) -> str:
    """Adds or updates an item in the store inventory."""
    payload = {
        "item_id": item_id,
        "item_name": item_name,
        "quantity": quantity,
        "price": price
    }
    res = requests.post(f"{BASE_URL}/store/{store_id}/update", json=payload)
    return res.text
def transfer_item_between_stores(from_store: str, to_store: str, item_id: int, quantity: int) -> str:
    """Transfers quantity of item from one store to another."""
    try:
        # Get both stores' data
        from_data = requests.get(f"{BASE_URL}/store/{from_store}").json()
        to_data = requests.get(f"{BASE_URL}/store/{to_store}").json()

        # Get item from source
        item = next((x for x in from_data if x["item_id"] == item_id), None)
        if not item:
            return f"Item {item_id} not found in {from_store}"

        if item["quantity"] < quantity:
            return f"Not enough quantity in {from_store} to transfer"

        # Reduce quantity in source store
        requests.post(f"{BASE_URL}/store/{from_store}/buy", json={"item_id": item_id, "quantity": quantity})

        # Check if item exists in destination
        item_to = next((x for x in to_data if x["item_id"] == item_id), None)

        if item_to:
            # Update existing item in destination
            new_quantity = item_to["quantity"] + quantity
        else:
            new_quantity = quantity  # First time addition

        # Update inventory in destination store
        payload = {
            "item_id": item_id,
            "item_name": item["item_name"],
            "quantity": new_quantity,
            "price": item["price"]
        }
        requests.post(f"{BASE_URL}/store/{to_store}/update", json=payload)

        return f"Transferred {quantity} units of item {item['item_name']} (ID {item_id}) from {from_store} to {to_store}"

    except Exception as e:
        return f"Transfer failed: {str(e)}"