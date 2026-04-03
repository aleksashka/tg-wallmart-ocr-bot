from aiogram import Router, F
from aiogram.types import Message

from utils import ocr
from utils.common import generate_filename
from utils.parse import ocr_to_receipt_items


router = Router()


@router.message(F.photo)
async def got_photo(message: Message):
    msg = await message.answer("Working on photo...")

    filename = generate_filename(tz_offset=-6)

    try:
        await message.bot.download(
            file=message.photo[-1].file_id,
            destination=filename,
        )
    except Exception as e:
        await msg.edit_text(f"Failed to download photo: {e}")
        return
    await msg.edit_text(f"Saved to {filename}")

    ocr_results = ocr.process_image(filename)
    receipt_items = ocr_to_receipt_items(ocr_results)
    list_of_str = [str(item) for item in receipt_items]
    await msg.edit_text("\n\n".join(list_of_str))
