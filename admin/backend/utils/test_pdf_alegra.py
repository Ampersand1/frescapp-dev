import requests
import os

# URL del API
url = 'https://api.alegra.com/api/v1/invoices/875?fields=pdf' 

# Encabezados de la petición
headers = {
    "authorization": "Basic dm1kaWFnb3ZAZ21haWwuY29tOjBmZmQ1YzdiM2NiMWI5OWVjNDA0"
}

# Realizar la solicitud GET
response = requests.get(url, headers=headers, stream=True)
print(response.json().get('pdf'))
# Verificar si la respuesta es exitosa
if response.status_code == 200:
    # Nombre del archivo PDF
    pdf_filename = "C:/Users/Usuario/Documents/frescapp/admin/backend/utils/invoice_875.pdf"

    # Guardar el archivo PDF
    with open(pdf_filename, "wb") as pdf_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                pdf_file.write(chunk)
    
    print(f"PDF descargado y guardado como: {pdf_filename}")
else:
    print(f"Error al descargar el PDF. Código de estado: {response.status_code}")

    