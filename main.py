import io
import os
import zipfile
from typing import List

import requests
from PIL import Image


def download_and_extract_archive(public_url: str, extract_path: str) -> None:
    """Скачиваем и распаковываем архив с Яндекс.Диска"""
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={public_url}"
    download_url = requests.get(api_url).json()["href"]

    with zipfile.ZipFile(io.BytesIO(requests.get(download_url).content)) as z:
        z.extractall(extract_path)


def create_tiff(
    images: List[Image.Image],
    output_path: str,
    images_per_row: int = 4,
    padding: int = 80,
) -> None:
    """
    Создаём .tif файл из полученных изображений,
    выстраиваем изображения по сетке, добавляем отступы
    """
    if not images:
        return

    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)
    num_rows = (len(images) + images_per_row - 1) // images_per_row

    grid_width = max_width * images_per_row + padding * (images_per_row + 1)
    grid_height = max_height * num_rows + padding * (num_rows + 1)

    grid_image = Image.new("RGB", (grid_width, grid_height), (255, 255, 255))

    for index, image in enumerate(images):
        row, col = divmod(index, images_per_row)

        offset = 0
        if row == num_rows - 1:
            num_images_in_last_row = (
                len(images) % images_per_row or images_per_row
            )
            total_padding = grid_width - (
                max_width * num_images_in_last_row
                + padding * (num_images_in_last_row + 1)
            )
            offset = total_padding // 2

        x = col * max_width + padding * (col + 1) + offset
        y = row * max_height + padding * (row + 1)

        grid_image.paste(image, (x, y))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    grid_image.save(output_path, save_all=True, compression="tiff_deflate")


def process_images(root_dir: str, output_dir: str) -> None:
    """Получаем изображения из всех подпапок и создаём .tif файлы"""
    for root, _, files in os.walk(root_dir):
        image_files = [
            os.path.join(root, file)
            for file in files
            if file.lower().endswith(("png", "jpg", "jpeg", "bmp", "gif"))
        ]

        if image_files:
            images = [Image.open(image_file) for image_file in image_files]
            folder_name = os.path.basename(root)
            output_path = os.path.join(output_dir, f"{folder_name}.tif")
            create_tiff(images, output_path)
            print(
                f"TIFF файл для папки '{folder_name}' создан и сохранён как '{output_path}'"
            )


def main():
    public_url = "https://disk.yandex.ru/d/V47MEP5hZ3U1kg"
    extract_path = "yandex_disk_content"
    output_dir = "tiff_files"

    download_and_extract_archive(public_url, extract_path)
    process_images(extract_path, output_dir)


if __name__ == "__main__":
    main()
