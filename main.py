from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote

app = FastAPI()

# Allow CORS for all origins (you can restrict this to specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-whatsapp/")
async def send_whatsapp(message_file: UploadFile = File(...), numbers_file: UploadFile = File(...)):
    # Save the uploaded files
    message_path = "message.txt"
    numbers_path = "numbers.txt"
    
    with open(message_path, "wb") as message_out, open(numbers_path, "wb") as numbers_out:
        message_out.write(await message_file.read())
        numbers_out.write(await numbers_file.read())
    
    # Read message content
    with open(message_path, 'r') as file:
        msg = file.read()
    msg = quote(msg)
    
    # Read numbers
    numbers = []
    with open(numbers_path, 'r') as file:
        for num in file.readlines():
            numbers.append(num.rstrip())

    # Start WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    link = "https://web.whatsapp.com"
    driver.get(link)
    time.sleep(20)  # Give time to scan QR code

    for num in numbers:
        try:
            link2 = f'https://web.whatsapp.com/send/?phone=91{num}&text={msg}'
            driver.get(link2)
            time.sleep(10)
            action = ActionChains(driver)
            action.send_keys(Keys.ENTER)
            action.perform()
            time.sleep(5)
        except Exception as e:
            return JSONResponse(content={"status": "error", "message": str(e)})
    
    driver.quit()
    return JSONResponse(content={"status": "success", "message": "Messages sent successfully!"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
