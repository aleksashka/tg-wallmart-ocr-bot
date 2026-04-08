import pytest
import numpy as np

from utils.models import ReceiptItem
from utils import parse


class TestParse:
    @pytest.mark.parametrize(
        "input_str, result",
        [
            ("S6.97D", (6.97, "D")),
            ("$4,470", (4.47, "D")),
            ("$4,47", (4.47, None)),
        ],
    )
    def test_parse_price_tax(self, input_str, result):
        assert parse.parse_price_tax(input_str) == result

    def test_ocr_to_receipt_items_simple(self):
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
        receipt_items = parse.ocr_to_receipt_items(ocr_results)
        assert receipt_items == expected_output

    def test_ocr_to_receipt_items_no_tax_code(self):
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
        ]

        expected_output = [
            ReceiptItem(
                name="AMBROSIA BAG",
                barcode="627735269640",
                price=6.97,
                tax_type=None,
            ),
        ]
        receipt_items = parse.ocr_to_receipt_items(ocr_results)
        assert receipt_items == expected_output
