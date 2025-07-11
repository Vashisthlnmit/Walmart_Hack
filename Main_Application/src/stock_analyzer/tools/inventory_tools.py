import requests
BASE_URL="http://localhost:8000"
def get_inventory_stock()->str:
     """Fetches the inventory data for reference"""
     res=requests.get(f"{BASE_URL}/inventory")
     return res.text

