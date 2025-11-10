import datetime
import subprocess

import google.generativeai as genai
import requests

genai.configure(api_key="AIzaSyCyC4sCbRLgjr9nEyjoKZqjOGPq9g8U2bE")

model = genai.GenerativeModel(model_name="gemini-2.0-flash")


def get_ssh_attempts():
    result = subprocess.check_output(
        "grep 'Failed Password' /var/log/auth.log | tail -n 18", shell=True
    )
    return result.decode("utf-8").split("\n")


def get_gemini_analysis(log_text):
    try:
        response = model.generate_content(
            f"Ada percobaan login brute force:\n{log_text}\nApa yang sebaiknya saya lakukan?, responnya jangan terlalu panjang"
        )
        return response.text
    except Exception as e:
        return f"Gagal mendapatkan analisis dari Gemini: {str(e)}"


def send_whatsapp(message):
    token = "UrZm39d6WQEN4Wm8CxKh"
    payload = {"target": "089631038443", "message": message}
    headers = {"Authorization": token}
    r = requests.post("https://api.fonnte.com/send", data=payload, headers=headers)
    return r.status_code


log = get_ssh_attempts()
ai_response = get_gemini_analysis(log)
full_message = (
    f"({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) {ai_response}"
)
send_whatsapp(full_message)
