from .models import ReceiptItem


BARCODE_LENGTH = 12


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
    barcode = price = tax_type = None

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

    tax_type = price_tax_list[-1]
    for old, new in (("0", "D"),):
        tax_type = tax_type.replace(old, new)

    price = "".join(price_tax_list[:-1])
    for old, new in (("S", ""), ("$", ""), (",", ".")):
        price = price.replace(old, new)

    result = ReceiptItem(
        name=" ".join(name_list),
        barcode=barcode,
        # price=float(price),
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


if __name__ == "__main__":
    import numpy as np

    ocr_results = [
        (
            [
                [np.int32(36), np.int32(3)],
                [np.int32(685), np.int32(3)],
                [np.int32(685), np.int32(68)],
                [np.int32(36), np.int32(68)],
            ],
            "AMBROSIA BAG 627735269640",
            np.float64(0.7453813979057209),
        ),
        (
            [
                [np.int32(826), 0],
                [np.int32(970), 0],
                [np.int32(970), np.int32(50)],
                [np.int32(826), np.int32(50)],
            ],
            "S6.97",
            np.float64(0.46366837282383055),
        ),
        (
            [
                [np.int32(986), np.int32(2)],
                [np.int32(1018), np.int32(2)],
                [np.int32(1018), np.int32(44)],
                [np.int32(986), np.int32(44)],
            ],
            "D",
            np.float64(0.39594129766175357),
        ),
        (
            [
                [np.int32(38), np.int32(80)],
                [np.int32(126), np.int32(80)],
                [np.int32(126), np.int32(128)],
                [np.int32(38), np.int32(128)],
            ],
            "ORG",
            np.float64(0.9958564793562332),
        ),
        (
            [
                [np.int32(142), np.int32(80)],
                [np.int32(198), np.int32(80)],
                [np.int32(198), np.int32(128)],
                [np.int32(142), np.int32(128)],
            ],
            "YL",
            np.float64(0.9984876005067481),
        ),
        (
            [
                [np.int32(215), np.int32(68)],
                [np.int32(685), np.int32(68)],
                [np.int32(685), np.int32(131)],
                [np.int32(215), np.int32(131)],
            ],
            "ONION 627735264580",
            np.float64(0.8981061747749168),
        ),
        (
            [
                [np.int32(828), np.int32(64)],
                [np.int32(970), np.int32(64)],
                [np.int32(970), np.int32(118)],
                [np.int32(828), np.int32(118)],
            ],
            "$4 , 47",
            np.float64(0.2561593998130806),
        ),
        (
            [
                [np.int32(992), np.int32(70)],
                [np.int32(1020), np.int32(70)],
                [np.int32(1020), np.int32(110)],
                [np.int32(992), np.int32(110)],
            ],
            "0",
            np.float64(0.35510696731434166),
        ),
    ]

    expected_output = [
        ReceiptItem(
            name="AMBROSIA BAG",
            barcode="627735269640",
            price=6.97,
            tax_type="D",
        ),
        ReceiptItem(
            name="ORG YL ONION",
            barcode="627735264580",
            price=4.47,
            tax_type="D",
        ),
    ]
    receipt_items = ocr_to_receipt_items(ocr_results)
    assert receipt_items == expected_output
    # for item in receipt_items:
    #     print(item)
    # ocr_to_receipt_items(width=1080, height=604)
    # output = get_rid_of_np(ocr_results)
    print("All tests are OK")
