"""Safe decimal-based calculator expression evaluator."""

from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass
from decimal import Decimal, DecimalException, localcontext
from typing import Callable


class CalculationError(ValueError):
    """An invalid or unsupported calculator expression."""


@dataclass(frozen=True)
class _Percent:
    value: Decimal


class ExpressionEvaluator:
    MAX_EXPRESSION_LENGTH = 250
    MAX_POWER = Decimal(1000)
    MAX_FACTORIAL = 500
    MAX_MAGNITUDE = Decimal("1e1000")

    def __init__(self, angle_unit: str = "deg", number_format: str = "id") -> None:
        if angle_unit not in {"deg", "rad"}:
            raise ValueError("angle_unit must be 'deg' or 'rad'")
        if number_format not in {"id", "international"}:
            raise ValueError("number_format must be 'id' or 'international'")
        self.angle_unit = angle_unit
        self.number_format = number_format

    def evaluate(self, expression: str, ans: Decimal | int | str = 0) -> Decimal:
        expression = expression.strip()
        if not expression:
            raise CalculationError("Masukkan ekspresi")
        if len(expression) > self.MAX_EXPRESSION_LENGTH:
            raise CalculationError("Ekspresi terlalu panjang")

        source = self._normalize(expression, self.number_format)
        try:
            tree = ast.parse(source, mode="eval")
            with localcontext() as context:
                context.prec = 28
                value = self._visit(tree.body, Decimal(str(ans)))
        except CalculationError:
            raise
        except (SyntaxError, DecimalException, ArithmeticError, OverflowError, ValueError) as error:
            message = str(error)
            if "division by zero" in message.lower() or "divisão por zero" in message.lower():
                raise CalculationError("Tidak dapat membagi dengan nol") from error
            raise CalculationError("Ekspresi tidak valid") from error

        if isinstance(value, _Percent):
            value = value.value
        self._check_magnitude(value)
        return value

    @staticmethod
    def _normalize(expression: str, number_format: str = "id") -> str:
        source = expression.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
        if number_format == "id":
            source = re.sub(
                r"\b\d{1,3}(?:\.\d{3}){2,}(?:,\d+)?\b|\b\d{1,3}\.\d{3},\d+\b",
                lambda match: match.group().replace(".", ""),
                source,
            )
            source = source.replace(",", ".")
        else:
            source = re.sub(
                r"\b\d{1,3}(?:,\d{3}){2,}(?:\.\d+)?\b|\b\d{1,3},\d{3}\.\d+\b",
                lambda match: match.group().replace(",", ""),
                source,
            )
            source = source.replace(",", "")
        source = source.replace("π", "pi")
        source = re.sub(r"(?<=\d)(?=\()", "*", source)
        source = re.sub(r"(?<=\))(?=\d|[A-Za-z])", "*", source)
        source = re.sub(r"(?<=\d)(?=(?:sqrt|sin|cos|tan|log|ln|pi|ans)\b|e\b(?![+-]?\d))", "*", source, flags=re.IGNORECASE)
        source = re.sub(r"(?<=\))(?=\()", "*", source)

        for symbol, function in (("%", "__pct__"), ("!", "factorial")):
            while symbol in source:
                position = source.find(symbol)
                start = ExpressionEvaluator._atom_start(source, position)
                atom = source[start:position].strip()
                if not atom:
                    raise CalculationError("Operator persen atau faktorial tidak memiliki nilai")
                source = source[:start] + f"{function}({atom})" + source[position + 1 :]
        return source

    @staticmethod
    def _atom_start(source: str, end: int) -> int:
        index = end - 1
        while index >= 0 and source[index].isspace():
            index -= 1
        if index < 0:
            return 0
        if source[index] == ")":
            depth = 1
            index -= 1
            while index >= 0 and depth:
                if source[index] == ")":
                    depth += 1
                elif source[index] == "(":
                    depth -= 1
                index -= 1
            return index + 1
        while index >= 0 and (source[index].isalnum() or source[index] in "._"):
            index -= 1
        return index + 1

    def _visit(self, node: ast.AST, ans: Decimal) -> Decimal | _Percent:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return Decimal(str(node.value))
        if isinstance(node, ast.Name):
            constants = {"pi": Decimal(str(math.pi)), "e": Decimal(str(math.e)), "ans": ans}
            if node.id.lower() in constants:
                return constants[node.id.lower()]
            raise CalculationError(f"Konstanta tidak dikenal: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = self._decimal(self._visit(node.operand, ans))
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = self._decimal(self._visit(node.left, ans))
            right_value = self._visit(node.right, ans)
            if isinstance(node.op, (ast.Add, ast.Sub)) and isinstance(right_value, _Percent):
                right = left * right_value.value
            else:
                right = self._decimal(right_value)
            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise CalculationError("Tidak dapat membagi dengan nol")
                result = left / right
            elif isinstance(node.op, ast.Pow):
                if abs(right) > self.MAX_POWER or (left == 0 and right < 0):
                    raise CalculationError("Pangkat di luar batas yang diizinkan")
                if right != right.to_integral_value() and left < 0:
                    raise CalculationError("Akar bilangan negatif tidak menghasilkan angka riil")
                result = left**int(right) if right == right.to_integral_value() else Decimal(str(float(left) ** float(right)))
            else:
                raise CalculationError("Operator tidak didukung")
            self._check_magnitude(result)
            return result
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == 1 and not node.keywords:
            name = node.func.id.lower()
            value = self._decimal(self._visit(node.args[0], ans))
            functions: dict[str, Callable[[float], float]] = {
                "sqrt": math.sqrt,
                "sin": lambda x: math.sin(math.radians(x) if self.angle_unit == "deg" else x),
                "cos": lambda x: math.cos(math.radians(x) if self.angle_unit == "deg" else x),
                "tan": lambda x: math.tan(math.radians(x) if self.angle_unit == "deg" else x),
                "log": math.log10,
                "ln": math.log,
                "abs": abs,
            }
            if name == "__pct__":
                return _Percent(value / Decimal(100))
            if name == "factorial":
                if value < 0 or value != value.to_integral_value() or value > self.MAX_FACTORIAL:
                    raise CalculationError("Faktorial hanya menerima bilangan bulat 0–500")
                return Decimal(math.factorial(int(value)))
            function = functions.get(name)
            if function is None:
                raise CalculationError(f"Fungsi tidak dikenal: {name}")
            try:
                result = function(float(value))
            except (ValueError, OverflowError) as error:
                raise CalculationError("Nilai di luar domain fungsi") from error
            if not math.isfinite(result):
                raise CalculationError("Hasil tidak terdefinisi")
            return Decimal(str(result))
        raise CalculationError("Ekspresi mengandung sintaks yang tidak didukung")

    @staticmethod
    def _decimal(value: Decimal | _Percent) -> Decimal:
        return value.value if isinstance(value, _Percent) else value

    def _check_magnitude(self, value: Decimal) -> None:
        if not value.is_finite() or abs(value) > self.MAX_MAGNITUDE:
            raise CalculationError("Hasil terlalu besar atau tidak terdefinisi")
