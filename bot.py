import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import zipfile
import logging
import asyncio
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Initialize the Pyrogram Client
API_ID = 26634100  # Replace with your actual API ID
API_HASH = "9ea49405d5a93e784114c469f5ce4bbd"  # Replace with your actual API Hash
BOT_TOKEN = "7643757891:AAHT4LVgW3pLeERQ7S4t6sxk_BnxRCQ89CQ"  # Replace with your actual Bot Token

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

file_queue = asyncio.Queue()
user_formats = {}

# Start command handler
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text('Hi! Send me a .cbz file, and I will extract it for you.')

@app.on_message(filters.command("file"))
async def set_file_format(client: Client, message: Message):
    try:
        format_string = message.text.split(" ", 1)[1]  # Get the format from the command
        user_formats[message.chat.id] = format_string
        await message.reply_text(f"File format set to: {format_string}")
    except IndexError:
        await message.reply_text("Please provide a format. Usage: /file [MY] [{episode}] Name @Manga_Yugen")

async def download_file(client: Client, file_id: str, file_name: str, message: Message) -> str:
    message1 = await client.send_message(message.chat.id, 'File downloading...')
    new_file = await client.download_media(file_id, file_name=f"{file_name}.cbz")
    await client.delete_messages(message.chat.id, message1.id)
    return new_file

async def extract_images(zip_path: str) -> list:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(zip_path))

    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    image_files = []

    for root, _, files in os.walk(os.path.dirname(zip_path)):
        for name in files:
            file_path = os.path.join(root, name)
            if name.lower().endswith(supported_extensions):
                image_files.append(file_path)
                logger.info(f"Found image: {file_path}")
            else:
                logger.warning(f"Unsupported image type: {name}")

    return image_files

def compress_image(image_path: str, output_path: str, quality: int = 75):
    """Compress the image and save it to the output path."""
    with Image.open(image_path) as img:
        img.save(output_path, format="JPEG", quality=quality, optimize=True)

def convert_images_to_pdf(image_files, pdf_output_path):
    if not image_files:
        logger.warning('No images provided for PDF conversion.')
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    thumb_image = os.path.join(script_dir, "thumb.jpg")

    if not os.path.exists(thumb_image):
        logger.error(f"Thumbnail image {thumb_image} not found.")
        return False

    c = canvas.Canvas(pdf_output_path)

    def draw_image(image_file):
        try:
            img = Image.open(image_file)
            img_width, img_height = img.size
            c.setPageSize((img_width, img_height))
            c.drawImage(image_file, 0, 0, width=img_width, height=img_height)
            c.showPage()
        except Exception as e:
            logger.error(f"Failed to process image {image_file}: {e}")

    draw_image(thumb_image)

    # Compress and draw each main image
    for image_file in image_files:
        compressed_image_path = image_file.replace(".", "_compressed.")
        compress_image(image_file, compressed_image_path, quality=75)  # Change quality as needed
        draw_image(compressed_image_path)
        os.remove(compressed_image_path)  # Remove the compressed version after use

    draw_image(thumb_image)

    c.save()
    logger.info(f"PDF created at {pdf_output_path}")
    return True

def cleanup_files(*file_paths):
    for file_path in file_paths:
        if os.path.isdir(file_path):
            for root, _, files in os.walk(file_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
            os.rmdir(file_path)
        elif os.path.isfile(file_path):
            os.remove(file_path)

@app.on_message(filters.command("cbz2pdf"))
async def cbz2pdf(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.document:
        file = message.reply_to_message.document

        try:
            file_name = file.file_name.rsplit('.', 1)[0]  # Remove file extension
            episode_number = file_name.split(" ")[-1]  # Assuming the episode number is the last part of the name
            episode_number = str(int(episode_number)).zfill(3)  # Convert to 3-digit format
        except IndexError:
            file_name = file.file_name
            episode_number = "000"  # Default to 000 if no episode number found

        if file.mime_type == 'application/x-cbr' or file.file_name.endswith('.cbz'):
            file_id = file.file_id
            await file_queue.put((file_id, file_name, message, episode_number))  # Store episode number in queue
            await message.reply_text(f'Added {file_name} to the processing queue. Queue size: {file_queue.qsize()}')
            logger.info(f'Added file id {file_id} with name {file_name} to the queue.')
        else:
            await message.reply_text('This document type is not supported.')
    else:
        await message.reply_text('Reply to this command with a document.')

async def process_files():
    while True:
        file_id, file_name, message, episode_number = await file_queue.get()  # Unpack the message and episode number
        try:
            new_file = await download_file(app, file_id, file_name, message)
            logger.info('File downloaded. Extracting images...')
            image_files = await extract_images(new_file)

            image_files.sort()
            logger.info(f"Total images found: {len(image_files)}")

            if not image_files:
                logger.warning('No images found in the .cbz file.')
                continue

            pdf_output_path = f"{file_name}.pdf"
            success = convert_images_to_pdf(image_files, pdf_output_path)

            if success:
                # Get the desired format or use a default one
                format_string = user_formats.get(message.chat.id, "[MY] [{episode}] {name} @Manga_Yugen")
                formatted_file_name = format_string.replace("{episode}", episode_number).replace("{name}", file_name)

                # Rename the PDF file
                os.rename(pdf_output_path, formatted_file_name + ".pdf")

                # Create the caption with HTML formatting
                caption = f"<blockquote><b>{formatted_file_name}</b></blockquote>"

                await app.send_document(message.chat.id, document=formatted_file_name + ".pdf", caption=caption, thumb=os.path.join(os.path.dirname(__file__), "thumbnail.jpg"))
                cleanup_files(new_file, formatted_file_name + ".pdf")
            else:
                logger.error("PDF conversion failed.")
        except Exception as e:
            logger.error(f'Error handling file: {e}', exc_info=True)
        finally:
            file_queue.task_done()


if __name__ == '__main__':
    app.start()
    loop = asyncio.get_event_loop()
    loop.create_task(process_files())
    try:
        loop.run_forever()
    finally:
        app.stop()
