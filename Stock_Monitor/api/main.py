from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "../data"

class Purchase(BaseModel):
    item_id: int
    quantity: int  # units bought
class ItemUpdate(BaseModel):
    item_id: int
    item_name: str
    quantity: int
    price: float
    last_updated: Optional[str] = None

# ----------------------------------------
# API 1: Get stock of a specific store
# ----------------------------------------
@app.get("/store/{store_id}")
def get_store_stock(store_id: str):
    try:
        file_path = os.path.join(DATA_DIR, f"{store_id}.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Store not found")

        df = pd.read_csv(file_path)
        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading store data: {str(e)}")

# ----------------------------------------
# API 2: Update stock after purchase
# ----------------------------------------
@app.post("/store/{store_id}/buy")
def update_stock(store_id: str, purchase: Purchase):
    try:
        file_path = os.path.join(DATA_DIR, f"{store_id}.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Store not found")

        df = pd.read_csv(file_path)

        if purchase.item_id not in df["item_id"].values:
            raise HTTPException(status_code=404, detail="Item not found in store")

        # Get index of the item
        idx = df[df["item_id"] == purchase.item_id].index[0]

        current_quantity = int(df.at[idx, "quantity"])

        if purchase.quantity > current_quantity:
            raise HTTPException(status_code=400, detail="Not enough stock available")

        # Update the quantity
        df.at[idx, "quantity"] = current_quantity - purchase.quantity

        # Save the updated CSV
        try:
            df.to_csv(file_path, index=False)
        except Exception as write_err:
            raise HTTPException(status_code=500, detail=f"Failed to write CSV: {write_err}")

        return {
            "message": "Purchase successful",
            "item_id": int(purchase.item_id),
            "remaining_quantity": int(df.at[idx, "quantity"])
        }

    except HTTPException as he:
        raise he  # Reraise HTTP errors without wrapping

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/store/{store_id}/update")
def update_inventory(store_id:str,item:ItemUpdate):
    try:
        file_path = os.path.join(DATA_DIR, f"{store_id}.csv")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Store not found")

        df = pd.read_csv(file_path)

        # Check if item exists
        if item.item_id in df["item_id"].values:
            idx = df[df["item_id"] == item.item_id].index[0]
            df.at[idx, "quantity"] = item.quantity
            df.at[idx, "price"] = item.price
            df.at[idx, "item_name"] = item.item_name
        else:
            new_row = {
                "item_id": item.item_id,
                "item_name": item.item_name,
                "quantity": item.quantity,
                "price": item.price,
                "last_updated": item.last_updated or pd.Timestamp.now().strftime("%Y-%m-%d")
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        df.to_csv(file_path, index=False)
        return {"message": "Inventory updated", "store_id": store_id, "item_id": item.item_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update inventory: {str(e)}") 

@app.get("/inventory")
def get_inventory_details():
        try:
            file_path = os.path.join(DATA_DIR, "inventory.csv")
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Inventory not found")
            df=pd.read_csv(file_path)
            return df.to_dict(orient='records')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading store data: {str(e)}")