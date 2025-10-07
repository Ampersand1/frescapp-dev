import requests
import os

# URL del API
url = 'https://api.alegra.com/api/v1/invoices/stamp' 

# Encabezados de la petición
headers = {
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"
}
payload = {'ids': [1942]}  # Reemplaza con los IDs de las facturas que deseas timbrar
# Realizar la solicitud GET
response = requests.post(url, headers=headers, json=payload)
print(response.text)
print(response.status_code)

    