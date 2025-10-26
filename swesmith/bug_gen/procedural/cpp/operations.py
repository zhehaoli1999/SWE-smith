"""
Operation-related procedural modifications for C++ code.
"""

import random

import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

from swesmith.bug_gen.procedural.base import CommonPMs
from swesmith.bug_gen.procedural.cpp.base import CppProceduralModifier
from swesmith.constants import BugRewrite, CodeEntity

CPP_LANGUAGE = Language(tscpp.language())

# Operator mappings for C++
FLIPPED_OPERATORS = {
    "==": "!=",
    "!=": "==",
    "<": ">=",
    "<=": ">",
    ">": "<=",
    ">=": "<",
    "&&": "||",
    "||": "&&",
}

ARITHMETIC_OPS = {"+", "-", "*", "/", "%"}
COMPARISON_OPS = {"<", ">", "<=", ">=", "==", "!="}
LOGICAL_OPS = {"&&", "||"}


class OperationChangeModifier(CppProceduralModifier):
    """Randomly change operations in C++ code."""

    explanation: str = CommonPMs.OPERATION_CHANGE.explanation
    name: str = CommonPMs.OPERATION_CHANGE.name
    conditions: list = CommonPMs.OPERATION_CHANGE.conditions

    def modify(self, code_entity: CodeEntity) -> BugRewrite | None:
        if not self.flip():
            return None

        parser = Parser(CPP_LANGUAGE)
        tree = parser.parse(bytes(code_entity.src_code, "utf8"))
        modified_code = self._change_operations(code_entity.src_code, tree.root_node)

        if modified_code == code_entity.src_code:
            return None

        return BugRewrite(
            rewrite=modified_code,
            explanation=self.explanation,
            strategy=self.name,
        )

    def _change_operations(self, code: str, node) -> str:
        """Change random operations in the code."""
        candidates = []
        self._find_operations(node, candidates)

        if not candidates:
            return code

        # Select a random operation to change
        target = random.choice(candidates)
        operator_text = code[target.start_byte : target.end_byte]

        # Choose a replacement from the same category
        replacement = None
        if operator_text in ARITHMETIC_OPS:
            ops = list(ARITHMETIC_OPS - {operator_text})
            replacement = random.choice(ops) if ops else None
        elif operator_text in COMPARISON_OPS:
            ops = list(COMPARISON_OPS - {operator_text})
            replacement = random.choice(ops) if ops else None
        elif operator_text in LOGICAL_OPS:
            ops = list(LOGICAL_OPS - {operator_text})
            replacement = random.choice(ops) if ops else None

        if replacement:
            return code[: target.start_byte] + replacement + code[target.end_byte :]

        return code

    def _find_operations(self, node, candidates):
        """Find all binary operators in the AST."""
        if node.type == "binary_expression":
            # In C++ tree-sitter, the operator is typically the 2nd child (after first operand)
            # We need to find the operator token
            for i, child in enumerate(node.children):
                # Check if this is an operator by looking for patterns
                if child.type in [
                    "+",
                    "-",
                    "*",
                    "/",
                    "%",
                    "<",
                    ">",
                    "<=",
                    ">=",
                    "==",
                    "!=",
                    "&&",
                    "||",
                ]:
                    candidates.append(child)
        for child in node.children:
            self._find_operations(child, candidates)


class OperationFlipOperatorModifier(CppProceduralModifier):
    """Flip comparison and logical operators."""

    explanation: str = CommonPMs.OPERATION_FLIP_OPERATOR.explanation
    name: str = CommonPMs.OPERATION_FLIP_OPERATOR.name
    conditions: list = CommonPMs.OPERATION_FLIP_OPERATOR.conditions

    def modify(self, code_entity: CodeEntity) -> BugRewrite | None:
        if not self.flip():
            return None

        parser = Parser(CPP_LANGUAGE)
        tree = parser.parse(bytes(code_entity.src_code, "utf8"))
        modified_code = self._flip_operators(code_entity.src_code, tree.root_node)

        if modified_code == code_entity.src_code:
            return None

        return BugRewrite(
            rewrite=modified_code,
            explanation=self.explanation,
            strategy=self.name,
        )

    def _flip_operators(self, code: str, node) -> str:
        """Flip comparison/logical operators."""
        candidates = []
        self._find_flippable_operators(node, candidates)

        if not candidates:
            return code

        target = random.choice(candidates)
        operator_text = code[target.start_byte : target.end_byte]

        if operator_text in FLIPPED_OPERATORS:
            replacement = FLIPPED_OPERATORS[operator_text]
            return code[: target.start_byte] + replacement + code[target.end_byte :]

        return code

    def _find_flippable_operators(self, node, candidates):
        """Find operators that can be flipped."""
        if node.type == "binary_expression":
            # The operator is typically a field in binary_expression in C++ tree-sitter
            # We need to look for operators in the structure
            for child in node.children:
                if child.type in FLIPPED_OPERATORS:
                    candidates.append(child)
        for child in node.children:
            self._find_flippable_operators(child, candidates)


class OperationSwapOperandsModifier(CppProceduralModifier):
    """Swap operands in commutative operations."""

    explanation: str = CommonPMs.OPERATION_SWAP_OPERANDS.explanation
    name: str = CommonPMs.OPERATION_SWAP_OPERANDS.name
    conditions: list = CommonPMs.OPERATION_SWAP_OPERANDS.conditions

    def modify(self, code_entity: CodeEntity) -> BugRewrite | None:
        if not self.flip():
            return None

        parser = Parser(CPP_LANGUAGE)
        tree = parser.parse(bytes(code_entity.src_code, "utf8"))
        modified_code = self._swap_operands(code_entity.src_code, tree.root_node)

        if modified_code == code_entity.src_code:
            return None

        return BugRewrite(
            rewrite=modified_code,
            explanation=self.explanation,
            strategy=self.name,
        )

    def _swap_operands(self, code: str, node) -> str:
        """Swap operands in binary expressions."""
        candidates = []
        self._find_binary_expressions(node, candidates)

        if not candidates:
            return code

        target = random.choice(candidates)
        if len(target.children) >= 3:
            left = target.children[0]
            right = target.children[2]

            left_text = code[left.start_byte : left.end_byte]
            right_text = code[right.start_byte : right.end_byte]

            # Reconstruct with swapped operands
            operator_node = target.children[1]
            operator_text = code[operator_node.start_byte : operator_node.end_byte]

            return (
                code[: left.start_byte]
                + right_text
                + " "
                + operator_text
                + " "
                + left_text
                + code[right.end_byte :]
            )

        return code

    def _find_binary_expressions(self, node, candidates):
        """Find binary expressions."""
        if node.type == "binary_expression" and len(node.children) >= 3:
            candidates.append(node)
        for child in node.children:
            self._find_binary_expressions(child, candidates)


class OperationChangeConstantsModifier(CppProceduralModifier):
    """Change numeric constants."""

    explanation: str = CommonPMs.OPERATION_CHANGE_CONSTANTS.explanation
    name: str = CommonPMs.OPERATION_CHANGE_CONSTANTS.name
    conditions: list = CommonPMs.OPERATION_CHANGE_CONSTANTS.conditions

    def modify(self, code_entity: CodeEntity) -> BugRewrite | None:
        if not self.flip():
            return None

        parser = Parser(CPP_LANGUAGE)
        tree = parser.parse(bytes(code_entity.src_code, "utf8"))
        modified_code = self._change_constants(code_entity.src_code, tree.root_node)

        if modified_code == code_entity.src_code:
            return None

        return BugRewrite(
            rewrite=modified_code,
            explanation=self.explanation,
            strategy=self.name,
        )

    def _change_constants(self, code: str, node) -> str:
        """Change numeric constants."""
        candidates = []
        self._find_numeric_literals(node, candidates)

        if not candidates:
            return code

        target = random.choice(candidates)
        original = code[target.start_byte : target.end_byte]

        try:
            if "." in original:
                value = float(original)
                new_value = value + random.choice([-1.0, 1.0, -0.1, 0.1])
            else:
                value = int(original, 0)  # Handles hex, octal, etc.
                new_value = value + random.choice([-1, 1, -10, 10])

            return code[: target.start_byte] + str(new_value) + code[target.end_byte :]
        except (ValueError, OverflowError):
            return code

    def _find_numeric_literals(self, node, candidates):
        """Find numeric literal nodes."""
        # C++ tree-sitter uses "number_literal" as a general type
        if node.type in [
            "number_literal",
            "decimal_literal",
            "binary_literal",
            "octal_literal",
            "hex_literal",
            "floating_literal",
        ]:
            candidates.append(node)
        for child in node.children:
            self._find_numeric_literals(child, candidates)


class OperationBreakChainsModifier(CppProceduralModifier):
    """Break method chains."""

    explanation: str = CommonPMs.OPERATION_BREAK_CHAINS.explanation
    name: str = CommonPMs.OPERATION_BREAK_CHAINS.name
    conditions: list = CommonPMs.OPERATION_BREAK_CHAINS.conditions

    def modify(self, code_entity: CodeEntity) -> BugRewrite | None:
        if not self.flip():
            return None

        parser = Parser(CPP_LANGUAGE)
        tree = parser.parse(bytes(code_entity.src_code, "utf8"))
        modified_code = self._break_chains(code_entity.src_code, tree.root_node)

        if modified_code == code_entity.src_code:
            return None

        return BugRewrite(
            rewrite=modified_code,
            explanation=self.explanation,
            strategy=self.name,
        )

    def _break_chains(self, code: str, node) -> str:
        """Break method call chains."""
        candidates = []
        self._find_method_chains(node, candidates)

        if not candidates:
            return code

        target = random.choice(candidates)
        # Remove one function call from the chain
        # In C++ tree-sitter, call_expression structure: [callee, arguments]
        if len(target.children) >= 1:
            # Keep just the callee part
            callee = target.children[0]
            return (
                code[: target.start_byte]
                + code[callee.start_byte : callee.end_byte]
                + code[target.end_byte :]
            )

        return code

    def _find_method_chains(self, node, candidates):
        """Find chained method calls."""
        # In C++ tree-sitter, function calls are "call_expression"
        if node.type == "call_expression":
            # Check if the callee is also a function call (chained)
            if node.children and node.children[0].type == "call_expression":
                candidates.append(node)
        for child in node.children:
            self._find_method_chains(child, candidates)
