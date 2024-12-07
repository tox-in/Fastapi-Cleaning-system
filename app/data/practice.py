import request
import pandas as pd

try:
    vehicle_api = request.get("http://localhost:8000/vehicle")
    vehicle_api.raise_for_status()
    vehicle_api_data = vehicle_api.json()
    vehicle_owners_api = request.get("http://localhost:8000/vehicle_owners_api")
    vehicle_owners_api.raise_for_status()
    vehicle_owners_api_data = vehicle_owners_api.json()

    vdf = pd.DataFrame(vehicle_api_data['vehicles'])
    odf = pd.DataFrame(vehicle_owners_api_data['owners'])

    vdf.to_csv('vehicles_data.csv', index=False)
    odf.to_csv('vehicles_owners_data.csv', index=False)
    print(vdf.shape, odf.shape)

    inner_merged_df = pd.merge(vdf, odf, on='vin', how='inner')
    inner_merged_df.to_csv('inner_merged_data.csv', index=False)
    print(inner_merged_df.shape)

except request.exceptions.RequestException as e:
    print(f"error {e}")









import request
import pandas as pd

try:
    vehicles_api=request.get("http://localhost:8080/vehicles")
    vehicles_api.raise_for_status()
    vehicles_data = vehicles_api.json()
    owners_api=request.get("http://localhost:8080/vehicles_owner")
    owners_api.raise_for_status()
    owners_data=owners_api.json()

    vdt=pd.DataFrame(vehicles_data['vehicles'])
    odt=pd.DataFrame(owners_data['owners'])

    vdt.to_csv("vehicles.csv", index=False)
    odt.to_csv("owners.csv", index=False)

    inner_merged_data=pd.merge(vdt,odt, on='vin', how='inner')
    inner_merged_data.to_csv("merged_data.csv", index=False)

except request.exceptions.RequestException as e:
    print(f"exception: {e}")
