from fastapi import FastAPI, File, Form, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import uvicorn
import os

app = FastAPI()
origins = [
    "https://laba-web-3.onrender.com",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def add_border(image_array, border_size):
    height, width, _ = image_array.shape
    new_height = height + 2 * border_size
    new_width = width + 2 * border_size
    new_image_array = np.zeros((new_height, new_width, 3), dtype=np.uint8)
    new_image_array[border_size:height+border_size, border_size:width+border_size] = image_array
    return new_image_array

def plot_color_distribution(image_array, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(image_array.flatten(), bins=256, range=(0, 256), color='b')
    ax.set_title(title)
    ax.set_xlabel('Значение пикселя')
    ax.set_ylabel('Количество пикселей')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')

# возвращаем основной обработанный шаблон index.html
@app.get("/", name="home")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# обрабатываем post запрос с данными формы и Captcha
@app.post("/process_image", name="process_image")
async def process_image(
    request: Request,
    image: UploadFile = File(...),
    border_size: int = Form(...)
):
    # Загружаем изображение
    image_bytes = await image.read()
    image_array = np.array(Image.open(BytesIO(image_bytes)))

    # Добавляем рамку к изображению
    image_array = add_border(image_array, border_size)

    # Сохраняем исходное изображение
    original_image = Image.fromarray(image_array)
    original_image_path = os.path.join("static", "original_image.png")
    original_image.save(original_image_path)
    print(f"Сохранено изображение: {original_image_path}")

    # Рисуем график распределения цветов для исходного изображения
    original_color_distribution = plot_color_distribution(image_array, "Распределение цветов исходного изображения")

    return templates.TemplateResponse("result.html", {
        "request": request,
        "original_image": "/static/original_image.png",
        "original_color_distribution": original_color_distribution,
    })

# запускаем локально веб сервер
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
