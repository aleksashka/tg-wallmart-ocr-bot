import easyocr


reader = easyocr.Reader(["en"], gpu=False, verbose=False)


def process_image(file_path: str, detail=1) -> list | str:
    """
    Parses the image and returns found text as a single string.
    """
    try:
        results = reader.readtext(file_path, detail=detail)
        return results
    except Exception as e:
        # Log the error in a real app
        return f"Error during OCR: {str(e)}"
