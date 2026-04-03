from .models import ReceiptItem


BARCODE_LENGTH = 12


def parse_price_tax(price_tax: str) -> tuple[float | None, str | None]:
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
    ['AMBROSIA BAG 627735269640', 'S6.97', 'D']
    ['ORG', 'YL', ONION 627735264580', '$4 , 47', '0']
    ['RB', 'PEPPERONI 072180763000', 'S5 ,97', 'D']
    ['KR', 'CHK', 'RIB', '068100078580', '52,78 D']
    ['QKR BG', '2,25k 055577101680', '$6,97']
    """
    print(texts)
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


def get_y_center(box):
    ys = [p[1] for p in box]
    return sum(ys) / len(ys)


def get_rid_of_np(np_result):
    result = []
    for box, text, confidence in np_result:
        new_box = [[int(x), int(y)] for x, y in box]
        result.append([new_box, text, float(confidence)])
    return result


def ocr_to_receipt_items(ocr_results):
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
