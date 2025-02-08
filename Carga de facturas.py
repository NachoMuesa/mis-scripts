from fastapi import FastAPI
import fitz  # PyMuPDF
import cv2
import easyocr
import numpy as np
import re
import json
import openai
from pyzbar.pyzbar import decode
import base64
from fastapi.responses import PlainTextResponse

# Configurar la clave de la API de OpenAI
openai.api_key = ""


def extract_qr_info(pdf_file_path):
    try:
        documento = fitz.open(pdf_file_path)
    except Exception as e:
        return None, str(e)

    primera_pagina = documento[0]
    imagen_pix = primera_pagina.get_pixmap(dpi=200, colorspace=fitz.csRGB)  # type: ignore
    image_np = np.frombuffer(imagen_pix.samples, dtype=np.uint8).reshape(
        imagen_pix.height, imagen_pix.width, 3
    )
    imagen_gris = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    codigos_qr = decode(imagen_gris)

    if not codigos_qr:
        return None, "No se encontró ningún código QR en el PDF"

    for codigo in codigos_qr:
        url = codigo.data.decode("utf-8")
        base64_encoded = url.split("p=")[-1]
        missing_padding = len(base64_encoded) % 4
        if missing_padding != 0:
            base64_encoded += "=" * (4 - missing_padding)

        try:
            base64_decoded = base64.b64decode(base64_encoded)
            decoded_str = base64_decoded.decode("utf-8")
            datos_factura = json.loads(decoded_str)

            # Determinar LETRA
            tipo_cmp = datos_factura.get("tipoCmp")
            if tipo_cmp in [1, 2, 3, 4, 5]:
                letra = "A"
            elif tipo_cmp in [6, 7, 8, 9, 10]:
                letra = "B"
            elif tipo_cmp in [11, 12, 13, 15, 16]:
                letra = "C"
            else:
                letra = "DESCONOCIDA"

            # Determinar TIPO_COMPROBANTE
            if tipo_cmp in [1, 6, 11]:
                tipo_comprobante = "FACTURA"
            elif tipo_cmp in [2, 7, 12]:
                tipo_comprobante = "NOTA DE DEBITO"
            elif tipo_cmp in [3, 8, 13]:
                tipo_comprobante = "NOTA DE CREDITO"
            elif tipo_cmp in [4, 9, 15]:
                tipo_comprobante = "RECIBO"
            else:
                tipo_comprobante = "DESCONOCIDO"

            # Modifico para que le de 1 si el cuit es del cjo y 0 caso que no encuentre compatibilidad
            cuit_cjo_original = datos_factura.get("nroDocRec")
            cuit_cjo_modificado = 1 if cuit_cjo_original == 30999253128 else 0

            return {
                "PV": datos_factura.get("ptoVta"),
                "NRO_FACTURA": datos_factura.get("nroCmp"),
                "CUIT": datos_factura.get("cuit"),
                "FECHA": datos_factura.get("fecha"),
                "IMPORTE": datos_factura.get("importe"),
                "TIPO_COMPROBANTE": tipo_comprobante,
                "LETRA": letra,
                "CUIT_CJO": cuit_cjo_modificado,
            }, None
        except (json.JSONDecodeError, base64.binascii.Error, UnicodeDecodeError) as e:  # type: ignore
            return None, f"ERROR en la decodificación del QR: {e}"


def extract_text_with_pymupdf(pdf_file_path):
    try:
        documento = fitz.open(pdf_file_path)
    except Exception as e:
        return None, str(e)

    if len(documento) == 0:
        return None, "El documento PDF está vacío."

    texto_completo = ""
    for pagina in documento:
        texto_completo += pagina.get_text("text") + "\n"  # type: ignore

    if not texto_completo.strip():
        return None, "No se pudo extraer texto del PDF."

    return texto_completo, None


def extract_text_with_ocr(pdf_file_path):
    try:
        documento = fitz.open(pdf_file_path)
    except Exception as e:
        return None, str(e)

    primera_pagina = documento[0]
    pix = primera_pagina.get_pixmap(dpi=300, colorspace=fitz.csRGB)  # type: ignore
    image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    reader = easyocr.Reader(["es"])
    result = reader.readtext(image_bgr)
    ocr_text = " ".join([text for _, text, _ in result])

    if not ocr_text.strip():
        return None, "No se pudo extraer texto mediante OCR."

    return ocr_text, None


def process_text_with_openai(texto):
    prompt = f"""Extract the following data from the invoice text:
        - CUIT in format 'XX-XXXXXXXX-X' or 'XXXXXXXXXXX'. If you find CUIT "30-99925312-8" or "30999253128" please ignore and find another cuit. Usually starts with '30' and the lenght of the digits is 11. Give this variable in a number format (without '""')
        - PV and NRO_FACTURA in this format 'XXXX-YYYYYYYY' where 'XXXX' (before "-") means PV and 'YYYYYYYY' (after "-") means NRO_FACTURA. Please, remove zeros before any number. Give this variables in a number format (without '""')
        - Date in dd-mm-yyyy format.
        - Amount as a number (use '.' for decimals). Usually you can find IMPORTE after "Total" word. Give this variable in a number format (without '""')
        - TIPO_COMPROBANTE is a variable that represents the invoice type. It usually comes with the word 'FACTURA' or 'NOTA DE CREDITO' or 'NOTA DE DEBITO'
          Returns the word that appears in the text.
        - LETRA: Invoice type as a letter ('A', 'B', 'C').
        - CUIT_CJO: if you find "30-99925312-8" or "30999253128" in this text, give "30999253128" else 0
        Example invoice text: {texto}

        Return the values in JSON format:
        {{
            "PV": value, 
            "NRO_FACTURA": value, 
            "CUIT": value, 
            "FECHA": value, 
            "IMPORTE": value, 
            "TIPO_COMPROBANTE": value,
            "LETRA": value,
            "CUIT_CJO": value
        }}"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant to extract information from invoices.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        if response.choices:
            extracted_data = response.choices[0].message.content
            extracted_data = re.sub(r"```json\n(.*)\n```", r"\1", extracted_data, flags=re.DOTALL)  # type: ignore
            data = json.loads(extracted_data)

            # Cambiamos el CUIT_CJO a 1 si es el CUIT del consejo, 0 si detecta cualquier cosa
            cuit_cjo_original = data.get("CUIT_CJO", 0)
            data["CUIT_CJO"] = 1 if cuit_cjo_original == 30999253128 else 0

            # Si CUIT_CJO = 1 y CUIT = 30999253128, entonces CUIT = 0
            cuit_arreglado = data.get("CUIT", 0)
            data["CUIT"] = (
                0
                if cuit_cjo_original == 1 and cuit_arreglado == 30999253128
                else cuit_arreglado
            )

            return data, None

    except json.JSONDecodeError:
        return None, "No se pudo decodificar el JSON de la API de OpenAI."
    except Exception as e:
        return None, str(e)

    return None, "No se obtuvo una respuesta válida de OpenAI."


def extract_from_folder(filename):
    data = []

    # 1. Intentar con QR
    qr_info, qr_error = extract_qr_info(filename)  # type: ignore
    if qr_info:
        qr_info["ARCHIVO"] = filename
        qr_info["FUENTE"] = "QR"
        qr_info["ERROR"] = None
        data.append(qr_info)
        return data

    # 2. Intentar con texto directo de PyMuPDF
    text, text_error = extract_text_with_pymupdf(filename)
    if text:
        processed_data, openai_error = process_text_with_openai(text)
        if processed_data:
            processed_data["ARCHIVO"] = filename
            processed_data["FUENTE"] = "TEXTO PDF"
            processed_data["ERROR"] = None
            data.append(processed_data)
            return data

    # 3. Intentar con OCR
    ocr_text, ocr_error = extract_text_with_ocr(filename)
    if ocr_text:
        processed_data, openai_error = process_text_with_openai(ocr_text)
        if processed_data:
            processed_data["ARCHIVO"] = filename
            processed_data["FUENTE"] = "OCR"
            processed_data["ERROR"] = None
            data.append(processed_data)
            return data

    # Si no se pudo extraer por ningún método
    data.append(
        {
            "ARCHIVO": filename,
            "FUENTE": "ERROR",
            "ERROR": qr_error or text_error or ocr_error,
            "DATOS": None,
        }
    )
    return data


def preparoarrayVb6(data):
    """
    Formatea y devuelve los datos en el formato solicitado, agregando saltos de línea entre registros.
    """
    resultado = []
    for item in data:
        resultado.append(f"ERROR:{item.get('ERROR', '')}")
        resultado.append(f"PV:{item.get('PV', '')}")
        resultado.append(f"NRO_FACTURA:{item.get('NRO_FACTURA', '')}")
        resultado.append(f"CUIT:{item.get('CUIT', '')}")
        resultado.append(f"FECHA:{item.get('FECHA', '')}")
        resultado.append(f"LETRA:{item.get('LETRA', '')}")
        resultado.append(f"TIPO_COMPROBANTE:{item.get('TIPO_COMPROBANTE', '')}")
        resultado.append(f"IMPORTE:{item.get('IMPORTE', '')}")
        resultado.append(f"CUIT_CJO:{item.get('CUIT_CJO', '')}")
        resultado.append(f"ARCHIVO:{item.get('ARCHIVO', '')}")
        resultado.append(f"FUENTE:{item.get('FUENTE', '')}")
        resultado.append("")

    return "\n".join(resultado).strip()


app = FastAPI()


@app.get("/lector", response_class=PlainTextResponse)
async def read_item(pdf: str):
    carpeta_pdfs = r"//server_file/fsdigitalizacion$/administracion/proceso proveedores/leccomprobantesvb6/"
    filename = carpeta_pdfs + pdf + ".pdf"
    data = extract_from_folder(filename)

    return preparoarrayVb6(data)
