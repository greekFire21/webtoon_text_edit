from PIL import Image, ImageDraw, ImageFont
import random
import pathlib
import json
import os
import argparse
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fonts_path",
        type=str,
        default="fonts",
    )
    parser.add_argument(
        "--images_path",
        type=str,
        default="data/original_images",
    )
    parser.add_argument(
        "--chars_path",
        type=str,
        default="chars.txt",
    )

    parser.add_argument(
        "--min_text_size",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--max_text_size",
        type=int,
        default=300,
    )
    parser.add_argument(
        "--min_text_length",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--max_text_length",
        type=int,
        default=7,
    )
    parser.add_argument(
        "--min_outline_width",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--max_outline_width",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--retry_count",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--input_images_path",
        type=str,
        default="data/input_images",
    )
    parser.add_argument(
        "--output_images_path",
        type=str,
        default="data/output_images",
    )
    parser.add_argument(
        "--json_path",
        type=str,
        default="data/data.json",
    )

    args = parser.parse_args()
    os.makedirs(args.input_images_path, exist_ok=True)
    os.makedirs(args.output_images_path, exist_ok=True)
    if args.retry_count < 0:
        raise ValueError("retry_count must be greater than 0.")

    return args


def main():
    args = parse_args()

    path = pathlib.Path(args.fonts_path)
    fonts = list(path.glob("*.ttf"))

    path = pathlib.Path(args.images_path)
    original_images_path = list(path.glob("*"))

    with open(args.chars_path, "r") as f:
        chars = f.read()
        chars = list(chars)

    for original_image_path in tqdm(original_images_path):
        # 이미지 열기
        input_image = Image.open(original_image_path).convert("RGB")
        input_draw = ImageDraw.Draw(input_image)
        output_image = Image.open(original_image_path).convert("RGB")

        # 이미지 크기 가져오기
        width, height = input_image.size

        # 텍스트 크기, 폰트, 색상 설정
        text_size = random.randint(args.min_text_size, args.max_text_size)
        text_font = random.choice(fonts)
        text_font = ImageFont.truetype(text_font, text_size)
        text_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        outline_width = random.randint(args.min_outline_width, args.max_outline_width)
        outline_color = random.choice([(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), (255, 255, 255), (0, 0, 0)])

        # 텍스트 길이 설정
        input_text_length = random.randint(args.min_text_length, args.max_text_length)
        
        # 텍스트 생성
        input_text = "".join(random.choices(chars, k=input_text_length))

        retry_count = 0
        retry_over = False
        while True:
            retry_count += 1
            if retry_count > args.retry_count:
                retry_over = True
                break

            try:
                # input_image 텍스트 그리기
                x0, y0, x1, y1 = input_draw.textbbox((0, 0), input_text, font=text_font)
                text_width, text_height = x1 - x0, y1 - y0
                char_width = text_width // len(input_text)
                text_height = int(text_height * random.randint(0, 100) / 100)

                x = random.randint(10, width - text_width - 10)
                y = random.randint(10, height - text_height * len(input_text) - 10)
            except Exception as e:
                text_size = random.randint(args.min_text_size, args.max_text_size)
                outline_width = random.randint(args.min_outline_width, args.max_outline_width)
                input_text_length = random.randint(args.min_text_length, args.max_text_length)
                input_text = "".join(random.choices(chars, k=input_text_length))
                continue

            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx**2 + dy**2 <= outline_width**2:
                        input_draw.text((x + dx, y + dy), input_text[0], font=text_font, fill=outline_color)
            x0, y0, x1, y1 = input_draw.textbbox((x, y), input_text[0], font=text_font)
            for i, char in enumerate(input_text):
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx**2 + dy**2 <= outline_width**2:
                            input_draw.text((x + i * char_width + dx, y + i * text_height + dy), char, font=text_font, fill=outline_color)
                _, _, x1, y1 = input_draw.textbbox((x + i * char_width, y + i * text_height), char, font=text_font)
                input_draw.text((x + i * char_width, y + i * text_height), char, font=text_font, fill=text_color)

            if x1 > width or y1 > height:
                # 이미지 열기
                input_image = Image.open(original_image_path).convert("RGB")
                input_draw = ImageDraw.Draw(input_image)
                output_image = Image.open(original_image_path).convert("RGB")
                continue

            crop_x0 = max(x0 - random.randint(0, 20), 0)
            crop_y0 = max(y0 - random.randint(0, 20), 0)
            crop_x1 = min(x1 + random.randint(0, 20), width)
            crop_y1 = min(y1 + random.randint(0, 20), height)

            cropped_input_image = input_image.crop((crop_x0, crop_y0, crop_x1, crop_y1))
            cropped_input_image.save(os.path.join(args.input_images_path, f"{original_image_path.stem}_input.jpg"))
            cropped_output_image = output_image.crop((crop_x0, crop_y0, crop_x1, crop_y1))
            cropped_output_image.save(os.path.join(args.output_images_path, f"{original_image_path.stem}_output.jpg"))
            break

        if retry_over:
            continue


        item = {"input_image": os.path.join(args.input_images_path, f"{original_image_path.stem}_input.jpg"),
                "output_image": os.path.join(args.output_images_path, f"{original_image_path.stem}_output.jpg"),
                "input_text": input_text,
                }

        with open(args.json_path, "a") as f:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

if __name__ == "__main__":
    main()