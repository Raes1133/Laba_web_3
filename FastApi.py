from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import io

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_form():
    with open("templates/form.html") as f:
        html_content = f.read()
    return html_content

@app.post("/process_image/")
async def process_image(image: UploadFile = File(...), period: int = Form(...), axis: str = Form(...)):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img_np = np.array(img) / 255.0

    width, height = img.size

    x = np.arange(width)
    y = np.arange(height)

    if axis == "horizontal":
        sin_wave = np.tile(np.sin(2 * np.pi * x / period), (height, 1))
    else:
        sin_wave = np.transpose(np.tile(np.sin(2 * np.pi * y / period), (width, 1)))

    modified_img = img_np * sin_wave
    modified_img = np.clip(modified_img, 0, 1)
    modified_img = Image.fromarray(np.uint8(modified_img * 255))

    # Сохраняем изображения
    img.save("static/original.png")
    modified_img.save("static/modified.png")

    # Создаем гистограммы
    fig, axs = plt.subplots(2, 1, figsize=(8, 8))

    axs[0].hist(img_np.ravel(), bins=256, range=(0, 1))
    axs[0].set_title("Original Image Histogram")
    axs[0].set_xlabel("Pixel Value")
    axs[0].set_ylabel("Frequency")

    axs[1].hist(modified_img.ravel(), bins=256, range=(0, 1))
    axs[1].set_title("Modified Image Histogram")
    axs[1].set_xlabel("Pixel Value")
    axs[1].set_ylabel("Frequency")

    plt.tight_layout()
    plt.savefig("static/histogram.png")

    return {
        "original_image_url": "/static/original.png",
        "modified_image_url": "/static/modified.png",
        "histogram_url": "/static/histogram.png",

    }
