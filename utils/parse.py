from .models import ReceiptItem


BARCODE_LENGTH = 12


def parse_price_tax(price_tax: str) -> tuple[float | None, str | None]:
    """
    Parse a raw price string with an optional tax suffix into numeric price and
    tax type.

    The function extracts a trailing tax indicator (if present) and normalizes
    the remaining string to convert it into a float.

    The price string is cleaned by:
    - removing "S" and "$" characters
    - replacing commas with dots

    If the price cannot be converted to a float, `None` is returned for the price.

    Args:
        price_tax (str): A raw string representing the price, optionally ending
            with a tax type character.

    Returns:
        tuple[float | None, str | None]: A tuple containing:
            - price (float | None): The parsed numeric value, or None if
                conversion fails
            - tax_type (str | None): The extracted tax type ("D", "E", "H"), or
                None if absent
    """
    price_str = price_tax
    if price_tax[-1] in "0DEH":
        tax_type = price_tax[-1]
        for old, new in (("0", "D"),):
            tax_type = tax_type.replace(old, new)
        price_str = price_tax[:-1]
    else:
        tax_type = None

    for old, new in (("S", ""), ("$", ""), (",", ".")):
        price_str = price_str.replace(old, new)
    try:
        price = float(price_str)
    except ValueError:
        price = None
    return price, tax_type


def line_to_receipt_item(texts: list[str]) -> ReceiptItem:
    """
    Parse OCR text fragments from a single line into a ReceiptItem.

    Splits text into words and extracts product name, barcode, and price/tax
    based on simple heuristics.

    Args:
        texts (list[str]): A list of OCR text fragments corresponding to a
            single line.

    Returns:
        ReceiptItem: An object containing parsed fields:
            - name (str): Product name
            - barcode (str | None): Detected barcode or None if not found
            - price (float | None): Parsed price or None if conversion fails
            - tax_type (str | None): Extracted tax type or None if absent
    """

    """
    ['AMBROSIA BAG 627735269640', 'S6.97', 'D']
    ['ORG', 'YL', ONION 627735264580', '$4 , 47', '0']
    ['RB', 'PEPPERONI 072180763000', 'S5 ,97', 'D']
    ['KR', 'CHK', 'RIB', '068100078580', '52,78 D']
    ['QKR BG', '2,25k 055577101680', '$6,97']
    """
    name_list = []
    price_tax_list = []
    barcode = None

    for text in texts:
        for word in text.split():
            if barcode is None:
                # Looking for a bar code line
                if len(word) < BARCODE_LENGTH:  # Too short
                    name_list.append(word)
                else:  # Length is enough
                    number_of_digits = sum(s.isdigit() for s in word)
                    if number_of_digits > int(BARCODE_LENGTH * 0.8):
                        barcode = word
                    else:
                        name_list.append(word)
            else:
                # Process as price and tax_type
                price_tax_list.append(word)

    price_tax_str = "".join(price_tax_list)
    price, tax_type = parse_price_tax(price_tax_str)

    result = ReceiptItem(
        name=" ".join(name_list),
        barcode=barcode,
        price=price,
        tax_type=tax_type,
    )
    return result


def get_y_center(box) -> float:
    """
    Calculate the vertical center (average y-coordinate) of a bounding box.

    The function takes a sequence of points representing a box and computes the
    mean of their y-coordinates.

    Args:
        box (iterable): A sequence of (x, y) coordinate pairs.

    Returns:
        float: The average y-coordinate of the box.
    """
    ys = [p[1] for p in box]
    return sum(ys) / len(ys)


def get_rid_of_np(np_result) -> list:
    """
    Takes an iterable of OCR results where each item contains:
    - box: coordinates (possibly NumPy types) representing a bounding box
    - text: the recognized text string
    - confidence: a numeric confidence score (possibly a NumPy type)

    It converts:
    - all box coordinates to integers
    - confidence values to float

    Args:
        np_result (iterable): An iterable of tuples/lists in the form
            (box, text, confidence), where box is a sequence of (x, y) pairs.

    Returns:
        list: A list of processed results in the form
            [[box, text, confidence], ...], where:
            - box is a list of [int, int] coordinate pairs
            - text is unchanged
            - confidence is a float
    """
    result = []
    for box, text, confidence in np_result:
        new_box = [[int(x), int(y)] for x, y in box]
        result.append([new_box, text, float(confidence)])
    return result


def ocr_to_receipt_items(ocr_results) -> list[ReceiptItem]:
    """
    Convert OCR output into structured receipt items grouped by text lines.

    This function processes raw OCR results containing bounding boxes, text, and
    confidence scores. It normalizes numeric types, estimates an average text
    box height, and uses it to determine line breaks based on vertical position
    (y-center of each box).

    Text elements are grouped into lines when their vertical centers are within
    a threshold distance. Each grouped line is then converted into a structured
    receipt item using `line_to_receipt_item`.

    Args:
        ocr_results (iterable): OCR output in the form of (box, text,
            confidence), where box is a sequence of (x, y) coordinates.

    Returns:
        list: A list of parsed receipt items, one per detected text line.
    """
    # Overall text box
    # min_x = min(coord[0] for item in ocr_results for coord in item[0])
    # max_x = max(coord[0] for item in ocr_results for coord in item[0])
    # min_y = min(coord[1] for item in ocr_results for coord in item[0])
    # max_y = max(coord[1] for item in ocr_results for coord in item[0])

    # Normalize integers and floats
    norm_results = get_rid_of_np(ocr_results)

    # Get heights of all boxes in ocr_results
    heights = [
        max(p[1] for p in box) - min(p[1] for p in box) for box, _, _ in norm_results
    ]
    avg_height = sum(heights) / len(heights)
    threshold = avg_height * 0.5  # To determine whether new line started

    current_line = []
    previous_y_center = -threshold

    result = []
    for box, text, _ in norm_results:
        current_y_center = get_y_center(box)
        if abs(current_y_center - previous_y_center) > threshold:
            # New line detected
            if current_line:  # Process only non-empty lines
                result.append(line_to_receipt_item(current_line))
            current_line = [text]
        else:
            current_line.append(text)
        previous_y_center = current_y_center
    # Do not forget to process the last line
    if current_line:
        result.append(line_to_receipt_item(current_line))
    return result
