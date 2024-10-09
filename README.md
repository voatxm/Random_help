
---

# CBZ to PDF Converter Bot

A Telegram bot that converts `.cbz` (Comic Book Archive) files into high-quality PDF files with user-defined naming formats. The bot ensures that all images inside the PDF maintain consistent width while keeping their original aspect ratio for height. Additionally, the bot adds a thumbnail image at the beginning and end of the PDF and compresses the images before conversion.

## Features

- **Convert CBZ to PDF**: Extracts images from `.cbz` files and compiles them into a single PDF.
- **Thumbnail Support**: Adds a custom thumbnail image at the start and end of the PDF.
- **File Naming Format**: Allows users to specify a custom naming format, replacing `{episode}` with the episode number from the original file name in 3-digit format.
- **Compression**: Compresses the images in the PDF to reduce file size by up to 50%.
- **No APIs Required**: All image processing and PDF conversion happen locally without the need for third-party API services.
- **Customizable width**: Images are resized to maintain a consistent width across the PDF, while the height is adjusted automatically.
- **Telegram Bot Integration**: Easy-to-use Telegram interface where users can send `.cbz` files and receive the PDF back.
- **Creator**: [@voatcb](https://t.me/voatcb)  
- **Telegram Channel**: [@Yugen_Bots](https://t.me/Yugen_Bots)

## Bot Commands

- `/start` - Starts the bot and displays a welcome message.
- `/cbz2pdf` - Send this command along with a `.cbz` file to convert it to PDF.
- `/file <format>` - Rename the output PDF using the specified format. The format should contain `{episode}`, which will be replaced with the 3-digit episode number from the original file name.

## Installation

### Prerequisites

- Python 3.8 or higher
- Termux or any Linux-based VPS
- Required libraries: `Pyrogram`, `Pillow`, `ReportLab`

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Install dependencies**:
   In the terminal, run the following command to install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the environment variables**:
   You need to set up your Telegram API credentials. Create a `.env` file in the root directory and add the following:
   ```env
   API_ID=<your_telegram_api_id>
   API_HASH=<your_telegram_api_hash>
   BOT_TOKEN=<your_bot_token>
   ```

4. **Run the bot**:
   To start the bot, simply run:
   ```bash
   python bot.py
   ```

### Deployment on Render.com

1. **Create a new Web Service**:
   - Go to [Render](https://render.com) and sign up.
   - Create a new **Web Service** and connect it to your GitHub repository.
   
2. **Set up environment variables**:
   Add the `API_ID`, `API_HASH`, and `BOT_TOKEN` as environment variables in the Render dashboard.

3. **Start the service**:
   Render will automatically detect your `requirements.txt` file and install the necessary dependencies. Once done, the bot will be deployed.

### Deployment on VPS

1. **Set up VPS**:
   If you're using a VPS like DigitalOcean or AWS EC2, make sure you have Python installed.

2. **Clone and install**:
   Follow the same steps as above to clone the repository and install dependencies.

3. **Run the bot**:
   Start the bot using:
   ```bash
   python bot.py
   ```

   Optionally, you can use tools like `screen` or `tmux` to keep the bot running even after disconnecting from SSH.

## Editing the Code

1. **Modifying File Naming Format**:
   - To change the way the bot names output files, you can modify the logic in the `/file` command handler inside `bot.py`.
   - Ensure `{episode}` is part of the format, which will be replaced with the episode number extracted from the `.cbz` file name.

2. **Customizing Compression**:
   - The compression logic for reducing the image size by 50% is located inside the `compress_images` function.
   - Adjust the compression settings to match your needs.

## License

This project is licensed under the MIT License.

## Creator

- [@voatcb](https://t.me/voatcb)
- [Telegram Channel](https://t.me/Yugen_Bots)

---

