import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.converter import convert
from core.evaluator import CalculationError, ExpressionEvaluator


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = ExpressionEvaluator()

    def test_acceptance_expressions(self):
        self.assertEqual(self.evaluator.evaluate("0.1 + 0.2"), Decimal("0.3"))
        self.assertEqual(self.evaluator.evaluate("2(3+4)"), Decimal(14))
        self.assertEqual(self.evaluator.evaluate("200 + 10%"), Decimal(220))
        self.assertEqual(self.evaluator.evaluate("2.500.000 + 1"), Decimal(2500001))
        self.assertEqual(self.evaluator.evaluate("2π").quantize(Decimal("0.000001")), Decimal("6.283185"))

    def test_basic_operators_and_parentheses(self):
        cases = {
            "2+3*4": 14,
            "(2+3)*4": 20,
            "8/2": 4,
            "2^8": 256,
            "-(4+2)": -6,
            "2,5 * 2": 5,
            "2.500,5 + 0,5": 2501,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(self.evaluator.evaluate(expression), Decimal(expected))

    def test_functions_constants_and_angle_modes(self):
        self.assertEqual(self.evaluator.evaluate("sqrt(144)"), Decimal(12))
        self.assertEqual(self.evaluator.evaluate("sin(30)"), Decimal("0.49999999999999994"))
        self.assertEqual(self.evaluator.evaluate("log(100)"), Decimal("2.0"))
        self.assertEqual(self.evaluator.evaluate("ln(e)"), Decimal("1.0"))
        self.assertEqual(self.evaluator.evaluate("2pi").quantize(Decimal("0.000001")), Decimal("6.283185"))
        self.assertEqual(ExpressionEvaluator("rad").evaluate("sin(pi/2)"), Decimal("1.0"))
        self.assertEqual(self.evaluator.evaluate("5!"), Decimal(120))
        self.assertEqual(self.evaluator.evaluate("2e"), Decimal("5.43656365691809"))
        self.assertEqual(self.evaluator.evaluate("2 + ans", 40), Decimal(42))

    def test_rejects_invalid_or_expensive_expressions(self):
        for expression in ("1/0", "9**9**9", "__import__('os')", "sqrt(-1)", "501!", "2+"):
            with self.subTest(expression=expression), self.assertRaises(CalculationError):
                self.evaluator.evaluate(expression)
        with self.assertRaises(CalculationError):
            self.evaluator.evaluate("1" * 251)

    def test_rejects_bool_literals(self):
        with self.assertRaises(CalculationError):
            self.evaluator.evaluate("True")


class ConverterTests(unittest.TestCase):
    def test_length_conversion_in_both_directions(self):
        self.assertEqual(convert(Decimal(1), "Panjang", "km", "m"), Decimal(1000))
        self.assertEqual(convert(Decimal(1000), "Panjang", "m", "km"), Decimal(1))

    def test_temperature_conversion(self):
        self.assertEqual(convert(Decimal(0), "Suhu", "°C", "°F"), Decimal(32))
        self.assertEqual(convert(Decimal(32), "Suhu", "°F", "°C"), Decimal(0))

    def test_international_number_format(self):
        evaluator = ExpressionEvaluator(number_format="international")
        self.assertEqual(evaluator.evaluate("1,234,567.5"), Decimal("1234567.5"))


class BroadArithmeticCases(unittest.TestCase):
    def test_one_hundred_integer_additions(self):
        evaluator = ExpressionEvaluator()
        for first in range(10):
            for second in range(10):
                expression = f"{first} + {second}"
                with self.subTest(expression=expression):
                    self.assertEqual(evaluator.evaluate(expression), Decimal(first + second))


if __name__ == "__main__":
    unittest.main()
