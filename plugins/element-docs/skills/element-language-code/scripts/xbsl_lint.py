#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


FORBIDDEN_1C8 = {
    "Процедура",
    "Функция",
    "КонецПроцедуры",
    "КонецФункции",
    "КонецЕсли",
    "КонецЦикла",
    "Тогда",
    "ИначеЕсли",
    "Новый",
}

DECLARATION_KEYWORDS = {
    "метод",
    "структура",
    "перечисление",
    "исключение",
    "пер",
    "знч",
    "исп",
    "конст",
}

BLOCK_KEYWORDS = {
    "метод",
    "если",
    "выбор",
    "для",
    "пока",
    "попытка",
    "структура",
    "перечисление",
    "исключение",
    "область",
}

BUILTIN_TYPES = {
    "Булево",
    "Число",
    "Строка",
    "Байты",
    "Дата",
    "Время",
    "ДатаВремя",
    "Длительность",
    "Момент",
    "Ууид",
    "Тип",
    "Null",
    "Неопределено",
    "неизвестно",
    "никогда",
    "ничто",
    "Объект",
    "Массив",
    "ЧитаемыйМассив",
    "Множество",
    "ЧитаемоеМножество",
    "Соответствие",
    "ЧитаемоеСоответствие",
    "Последовательность",
    "Обходимое",
    "Исключение",
    "ИсключениеНедопустимыйАргумент",
    "Закрываемое",
    "ЧасовойПояс",
}

BUILTIN_VALUES = {
    "Истина": "Булево",
    "Ложь": "Булево",
    "Неопределено": "Неопределено",
    "Null": "Null",
}

TYPE_LITERAL_NAMES = {
    "Байты",
    "Дата",
    "Время",
    "ДатаВремя",
    "Ууид",
    "ЧасовойПояс",
}

ASSIGNMENT_OPERATORS = {"=", "+=", "-=", "*=", "/="}
PROJECT_CONTEXT_SUPPRESSED_CODES = {
    "XBSL0002",
    "XBSL0007",
    "XBSL0008",
    "XBSL0009",
    "XBSL0010",
    "XBSL0013",
    "XBSL0014",
}


@dataclass(frozen=True)
class Diagnostic:
    path: str
    line: int
    column: int
    severity: str
    code: str
    message: str

    def to_json(self) -> dict[str, object]:
        return {
            "path": self.path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int
    index: int

    @property
    def end_marker(self) -> bool:
        return self.kind == "EOF"


EOF_TOKEN = Token("EOF", "<eof>", 1, 1, -1)


class Lexer:
    def __init__(self, text: str, path: str) -> None:
        self.text = text
        self.path = path
        self.index = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []

    def tokenize(self) -> tuple[list[Token], list[Diagnostic]]:
        while not self.at_end:
            char = self.peek_char()
            if char in " \t\r":
                self.advance_char()
            elif char == "\n":
                self.add_token("NEWLINE", "\n")
                self.advance_char()
            elif char == "/" and self.peek_char(1) == "/":
                self.skip_comment()
            elif char in {'"', "'"}:
                self.read_string()
            elif char.isdigit():
                self.read_number()
            elif is_identifier_start(char):
                self.read_identifier()
            else:
                self.read_symbol_or_operator()

        self.tokens.append(Token("EOF", "<eof>", self.line, self.column, self.index))
        return self.tokens, self.diagnostics

    @property
    def at_end(self) -> bool:
        return self.index >= len(self.text)

    def peek_char(self, offset: int = 0) -> str:
        position = self.index + offset
        return self.text[position] if position < len(self.text) else "\0"

    def advance_char(self) -> str:
        char = self.text[self.index]
        self.index += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def add_token(self, kind: str, value: str, line: int | None = None, column: int | None = None, index: int | None = None) -> None:
        self.tokens.append(Token(kind, value, line or self.line, column or self.column, self.index if index is None else index))

    def add_diagnostic(self, token: Token, code: str, message: str) -> None:
        self.diagnostics.append(Diagnostic(self.path, token.line, token.column, "ERROR", code, message))

    def skip_comment(self) -> None:
        while not self.at_end and self.peek_char() != "\n":
            self.advance_char()

    def read_string(self) -> None:
        start_line = self.line
        start_column = self.column
        start_index = self.index
        quote = self.peek_char()
        value = self.advance_char()
        escaped = False
        interpolation_depth = 0
        interpolation_quote: str | None = None
        interpolation_escaped = False
        while not self.at_end:
            char = self.advance_char()
            value += char
            if interpolation_depth > 0:
                if interpolation_quote is not None:
                    if interpolation_escaped:
                        interpolation_escaped = False
                    elif char == "\\":
                        interpolation_escaped = True
                    elif char == interpolation_quote:
                        interpolation_quote = None
                    continue
                if char in {'"', "'"}:
                    interpolation_quote = char
                elif char == "{":
                    interpolation_depth += 1
                elif char == "}":
                    interpolation_depth -= 1
                continue
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char in {"%", "$"} and self.peek_char() == "{":
                value += self.advance_char()
                interpolation_depth = 1
            elif char == quote:
                self.tokens.append(Token("STRING", value, start_line, start_column, start_index))
                return

        token = Token("STRING", value, start_line, start_column, start_index)
        self.tokens.append(token)
        self.add_diagnostic(token, "XBSL0002", "Строковый литерал не закрыт.")

    def read_number(self) -> None:
        start_line = self.line
        start_column = self.column
        start_index = self.index
        value = ""
        while self.peek_char().isdigit():
            value += self.advance_char()
        if self.peek_char() == "." and self.peek_char(1).isdigit():
            value += self.advance_char()
            while self.peek_char().isdigit():
                value += self.advance_char()
        self.tokens.append(Token("NUMBER", value, start_line, start_column, start_index))

    def read_identifier(self) -> None:
        start_line = self.line
        start_column = self.column
        start_index = self.index
        value = ""
        while is_identifier_continue(self.peek_char()):
            value += self.advance_char()
        token = Token("IDENT", value, start_line, start_column, start_index)
        self.tokens.append(token)
        if not (self.peek_char() == "{" and value):
            return
        literal = self.read_braced_literal(value, start_line, start_column, start_index)
        self.tokens[-1] = literal

    def read_braced_literal(self, prefix: str, start_line: int, start_column: int, start_index: int) -> Token:
        value = prefix
        depth = 0
        in_string = False
        escaped = False
        while not self.at_end:
            char = self.advance_char()
            value += char
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return Token("BRACED_LITERAL", value, start_line, start_column, start_index)
        token = Token("BRACED_LITERAL", value, start_line, start_column, start_index)
        self.add_diagnostic(token, "XBSL0002", f"Литерал '{prefix}{{...}}' не закрыт.")
        return token

    def read_symbol_or_operator(self) -> None:
        start_line = self.line
        start_column = self.column
        start_index = self.index
        two = self.peek_char() + self.peek_char(1)
        if two in {"==", "!=", ">=", "<=", "+=", "-=", "*=", "/=", "**", "??", "?.", "->", "::"}:
            self.advance_char()
            self.advance_char()
            self.tokens.append(Token("OP", two, start_line, start_column, start_index))
            return
        char = self.advance_char()
        kind = "SYMBOL" if char in "()[]{}.,:;@<>?|=+-*/%&" else "UNKNOWN"
        self.tokens.append(Token(kind, char, start_line, start_column, start_index))


def is_identifier_start(char: str) -> bool:
    return char == "_" or char.isalpha()


def is_identifier_continue(char: str) -> bool:
    return char == "_" or char.isalpha() or char.isdigit()


@dataclass(frozen=True)
class TypeRef:
    text: str
    token: Token
    identifiers: tuple[str, ...] = ()
    has_invalid_undefined: bool = False
    dotted: bool = False

    def to_type(self) -> "XbslType":
        if not self.text:
            return XbslType.unknown()
        if self.text.startswith("(") and "->" in self.text:
            return XbslType({"функция"})
        names: set[str] = set()
        for part in split_union_type(self.text):
            clean = part.strip()
            if not clean:
                continue
            if clean == "?":
                names.add("Неопределено")
                continue
            if clean.endswith("?"):
                clean = clean[:-1]
                names.add("Неопределено")
            base = base_type_name(clean)
            if base:
                names.add(base)
        return XbslType(names) if names else XbslType.unknown()


@dataclass(frozen=True)
class XbslType:
    names: frozenset[str] = field(default_factory=frozenset)
    unknown: bool = False

    def __init__(self, names: Iterable[str] | None = None, unknown: bool = False) -> None:
        object.__setattr__(self, "names", frozenset(names or ()))
        object.__setattr__(self, "unknown", unknown)

    @staticmethod
    def unknown() -> "XbslType":
        return XbslType(unknown=True)

    @staticmethod
    def nothing() -> "XbslType":
        return XbslType({"ничто"})

    def display(self) -> str:
        if self.unknown:
            return "неизвестно"
        return "|".join(sorted(self.names)) or "неизвестно"


@dataclass
class Param:
    name: str
    type_ref: TypeRef
    default: "Expr | None"
    token: Token


@dataclass
class Module:
    path: str
    declarations: list["Decl"]


class Decl:
    token: Token


@dataclass
class MethodDecl(Decl):
    name: str
    params: list[Param]
    return_type: TypeRef | None
    body: list["Stmt"]
    token: Token
    static: bool = False
    annotations: tuple[str, ...] = ()
    abstract: bool = False


@dataclass
class VarDecl(Decl):
    kind: str
    name: str
    type_ref: TypeRef | None
    initializer: "Expr | None"
    token: Token
    required: bool = False


@dataclass
class TypeDecl(Decl):
    kind: str
    name: str
    members: list[Decl]
    token: Token
    annotations: tuple[str, ...] = ()


@dataclass
class EnumDecl(Decl):
    name: str
    values: list[str]
    token: Token
    annotations: tuple[str, ...] = ()


class Stmt:
    token: Token


@dataclass
class IfStmt(Stmt):
    condition: "Expr"
    then_body: list[Stmt]
    elifs: list[tuple["Expr", list[Stmt]]]
    else_body: list[Stmt]
    token: Token


@dataclass
class WhileStmt(Stmt):
    condition: "Expr"
    body: list[Stmt]
    token: Token


@dataclass
class ForStmt(Stmt):
    name: str | None
    header_tokens: list[Token]
    body: list[Stmt]
    token: Token


@dataclass
class ChoiceStmt(Stmt):
    expression: "Expr | None"
    branches: list[tuple["Expr | None", list[Stmt]]]
    else_body: list[Stmt]
    token: Token


@dataclass
class TryStmt(Stmt):
    body: list[Stmt]
    catches: list[tuple[str | None, TypeRef | None, list[Stmt]]]
    finally_body: list[Stmt]
    token: Token


@dataclass
class BlockStmt(Stmt):
    body: list[Stmt]
    token: Token


@dataclass
class ReturnStmt(Stmt):
    value: "Expr | None"
    token: Token


@dataclass
class ThrowStmt(Stmt):
    value: "Expr | None"
    token: Token


@dataclass
class BreakContinueStmt(Stmt):
    kind: str
    token: Token


@dataclass
class AssignStmt(Stmt):
    target: "Expr"
    operator: str
    value: "Expr"
    token: Token


@dataclass
class ExprStmt(Stmt):
    expr: "Expr"
    token: Token


class Expr:
    token: Token


@dataclass
class UnknownExpr(Expr):
    token: Token = EOF_TOKEN


@dataclass
class LiteralExpr(Expr):
    type_name: str
    token: Token


@dataclass
class NameExpr(Expr):
    name: str
    token: Token


@dataclass
class UnaryExpr(Expr):
    operator: str
    operand: Expr
    token: Token


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: str
    right: Expr
    token: Token


@dataclass
class TernaryExpr(Expr):
    condition: Expr
    when_true: Expr
    when_false: Expr
    token: Token


@dataclass
class MemberExpr(Expr):
    obj: Expr
    name: str
    safe: bool
    token: Token


@dataclass
class IndexExpr(Expr):
    obj: Expr
    index: Expr
    token: Token


@dataclass
class Arg:
    name: str | None
    value: Expr
    token: Token


@dataclass
class CallExpr(Expr):
    callee: Expr
    args: list[Arg]
    token: Token


@dataclass
class NewExpr(Expr):
    type_ref: TypeRef
    args: list[Arg]
    token: Token


@dataclass
class TypeCheckExpr(Expr):
    value: Expr
    type_ref: TypeRef
    negated: bool
    token: Token


@dataclass
class CastExpr(Expr):
    value: Expr
    type_ref: TypeRef
    token: Token


@dataclass
class CollectionExpr(Expr):
    kind: str
    elements: list[Expr]
    token: Token
    type_ref: TypeRef | None = None


@dataclass
class LambdaExpr(Expr):
    params: list[Param]
    body: list[Stmt]
    return_expr: Expr | None
    token: Token


class Parser:
    def __init__(self, tokens: list[Token], path: str, diagnostics: list[Diagnostic]) -> None:
        self.tokens = tokens
        self.path = path
        self.diagnostics = diagnostics
        self.current = 0

    def parse(self) -> Module:
        declarations: list[Decl] = []
        while not self.peek().end_marker:
            self.skip_newlines()
            if self.peek().end_marker:
                break
            if self.match_value(";"):
                self.error(self.previous(), "XBSL0004", "Лишний символ ';': нет открытого блока, который он закрывает.")
                continue
            annotations = self.parse_annotations()
            if self.peek().end_marker:
                break
            if self.match_value("импорт"):
                self.consume_header_tail()
                continue
            if self.check_forbidden_1c8_construct():
                self.report_forbidden_1c8_construct(self.advance())
                self.skip_line()
                continue
            decl = self.parse_declaration(annotations, top_level=True)
            if decl is not None:
                declarations.append(decl)
            else:
                self.error(self.peek(), "XBSL0002", f"Неожиданная конструкция верхнего уровня '{self.peek().value}'.")
                self.skip_line()
        return Module(self.path, declarations)

    def parse_declaration(self, annotations: list[str], top_level: bool) -> Decl | None:
        if self.check_value("абстрактный") or self.check_value("статический") or self.check_value("метод"):
            return self.parse_method(annotations)
        if self.check_value("конструктор"):
            return self.parse_constructor(annotations)
        if self.check_value("структура"):
            return self.parse_type_decl("структура", annotations)
        if self.check_value("исключение"):
            return self.parse_type_decl("исключение", annotations)
        if self.check_value("перечисление"):
            return self.parse_enum(annotations)
        if self.check_value("обз") or self.check_value("пер") or self.check_value("знч") or self.check_value("исп") or self.check_value("конст"):
            return self.parse_var_decl(allow_required=not top_level)
        return None

    def parse_annotations(self) -> list[str]:
        annotations: list[str] = []
        while True:
            self.skip_newlines()
            if not self.match_value("@"):
                return annotations
            name = self.expect_ident("Ожидалось имя аннотации после '@'.")
            if name:
                annotations.append(name.value)
            if self.match_value("("):
                self.skip_balanced("(", ")")
            self.skip_newlines()

    def parse_method(self, annotations: list[str]) -> MethodDecl:
        abstract = self.match_value("абстрактный")
        static = self.match_value("статический")
        token = self.expect_value("метод", "Ожидалось ключевое слово 'метод'.") or self.peek()
        name_token = self.expect_ident("Ожидалось имя метода.")
        name = name_token.value if name_token else "<error>"
        params: list[Param] = []
        if self.expect_value("(", "Ожидался список параметров метода в скобках."):
            params = self.parse_params()
            self.expect_value(")", "Список параметров метода не закрыт ')'.")
        return_type = None
        if self.match_value(":"):
            type_tokens = self.collect_type_until_values({"\n"})
            return_type = make_type_ref(type_tokens, token)
        else:
            self.consume_header_tail()
        if abstract:
            return MethodDecl(name, params, return_type, [], token, static, tuple(annotations), abstract)
        body = self.parse_statements_until(set())
        self.expect_block_close(token, "метод")
        return MethodDecl(name, params, return_type, body, token, static, tuple(annotations), abstract)

    def parse_constructor(self, annotations: list[str]) -> MethodDecl:
        token = self.expect_value("конструктор", "Ожидалось ключевое слово 'конструктор'.") or self.peek()
        params: list[Param] = []
        if self.match_value("("):
            params = self.parse_params()
            self.expect_value(")", "Список параметров конструктора не закрыт ')'.")
        self.consume_header_tail()
        return MethodDecl("конструктор", params, None, [], token, False, tuple(annotations))

    def parse_params(self) -> list[Param]:
        params: list[Param] = []
        self.skip_newlines()
        while not self.peek().end_marker and not self.check_value(")"):
            token = self.expect_ident("Ожидалось имя параметра.")
            name = token.value if token else "<error>"
            if self.match_value(":"):
                type_tokens = self.collect_type_until_values({",", ")", "="})
                type_ref = make_type_ref(type_tokens, token or self.peek())
            else:
                type_ref = TypeRef("неизвестно", token or self.peek(), ("неизвестно",))
            default = None
            if self.match_value("="):
                default = parse_expr_tokens(self.collect_default_expr_until_values({",", ")"}), self.path, self.diagnostics)
            params.append(Param(name, type_ref, default, token or self.peek()))
            if not self.match_value(","):
                break
            self.skip_newlines()
        return params

    def parse_type_decl(self, kind: str, annotations: list[str]) -> TypeDecl:
        type_annotations = tuple(annotations)
        token = self.expect_value(kind, f"Ожидалось ключевое слово '{kind}'.") or self.peek()
        name_token = self.expect_ident(f"Ожидалось имя {kind}.")
        name = name_token.value if name_token else "<error>"
        self.consume_header_tail()
        members: list[Decl] = []
        while not self.peek().end_marker:
            self.skip_newlines()
            if self.check_value(";"):
                break
            member_annotations = self.parse_annotations()
            member = self.parse_declaration(member_annotations, top_level=False)
            if member is not None:
                members.append(member)
            else:
                self.error(self.peek(), "XBSL0002", f"Неожиданная конструкция в {kind}: '{self.peek().value}'.")
                self.skip_line()
        self.expect_block_close(token, kind)
        return TypeDecl(kind, name, members, token, type_annotations)

    def parse_enum(self, annotations: list[str]) -> EnumDecl:
        token = self.expect_value("перечисление", "Ожидалось ключевое слово 'перечисление'.") or self.peek()
        name_token = self.expect_ident("Ожидалось имя перечисления.")
        name = name_token.value if name_token else "<error>"
        values: list[str] = []
        while not self.peek().end_marker:
            self.skip_newlines()
            if self.check_value(";"):
                break
            if self.check_value("@"):
                self.parse_annotations()
                continue
            if self.check_ident():
                values.append(self.advance().value)
                if self.check_value("умолчание"):
                    self.advance()
                self.match_value(",")
            else:
                self.error(self.peek(), "XBSL0002", f"Неожиданный токен в перечислении: '{self.peek().value}'.")
                self.advance()
        self.expect_block_close(token, "перечисление")
        return EnumDecl(name, values, token, tuple(annotations))

    def parse_var_decl(self, allow_required: bool) -> VarDecl:
        required = False
        if self.match_value("обз"):
            required = True
            if not allow_required:
                self.error(self.previous(), "XBSL0005", "'обз' допустимо только для полей структур и исключений.")
        token = self.peek()
        if not (self.match_value("пер") or self.match_value("знч") or self.match_value("исп") or self.match_value("конст")):
            self.error(self.peek(), "XBSL0005", "Ожидался модификатор объявления: пер, знч, исп или конст.")
            self.advance()
        kind = self.previous().value
        name_token = self.expect_ident("Ожидалось имя переменной.")
        name = name_token.value if name_token else "<error>"
        type_ref = None
        initializer = None
        if self.match_value(":"):
            type_tokens = self.collect_type_until_values({"=", "\n"})
            type_ref = make_type_ref(type_tokens, name_token or token)
        if self.match_value("="):
            init_tokens = self.collect_expression_tokens()
            if is_block_lambda_header(init_tokens):
                arrow_index = top_level_arrow_index(init_tokens) or 0
                if init_tokens and init_tokens[0].value == "метод":
                    initializer = LambdaExpr(
                        parse_lambda_params(init_tokens[:arrow_index]),
                        self.parse_statements_until(set()),
                        None,
                        init_tokens[0],
                    )
                    self.expect_block_close(init_tokens[0], "лямбда")
                else:
                    initializer = LambdaExpr(
                        parse_lambda_params(init_tokens[:arrow_index]),
                        [],
                        parse_expr_tokens(self.collect_expression_tokens(), self.path, self.diagnostics),
                        init_tokens[0],
                    )
            else:
                initializer = parse_expr_tokens(init_tokens, self.path, self.diagnostics)
        else:
            self.consume_line_end()
        if type_ref is None and initializer is None:
            self.error(token, "XBSL0005", "Объявление без инициализации должно явно указывать тип.")
        return VarDecl(kind, name, type_ref, initializer, token, required)

    def parse_statements_until(self, stoppers: set[str]) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.peek().end_marker:
            self.skip_newlines()
            if self.peek().end_marker or self.check_value(";") or self.peek().value in stoppers:
                break
            annotations = self.parse_annotations()
            if annotations and (self.check_value("абстрактный") or self.check_value("статический") or self.check_value("метод")):
                statements.append(self.parse_method(annotations))
                continue
            statement = self.parse_statement()
            if statement is not None:
                statements.append(statement)
            else:
                self.error(self.peek(), "XBSL0002", f"Неожиданная инструкция '{self.peek().value}'.")
                self.skip_line()
        return statements

    def parse_statement(self) -> Stmt | None:
        if self.check_forbidden_1c8_construct():
            self.report_forbidden_1c8_construct(self.advance())
            self.skip_line()
            return None
        if self.check_value("если") or self.check_value("if"):
            return self.parse_if()
        if self.check_value("выбор"):
            return self.parse_choice()
        if self.check_value("пока"):
            return self.parse_while()
        if self.check_value("для"):
            return self.parse_for()
        if self.check_value("попытка"):
            return self.parse_try()
        if self.check_value("область"):
            return self.parse_block()
        if self.check_value("возврат"):
            token = self.advance()
            tokens = self.collect_expression_tokens()
            return ReturnStmt(parse_expr_tokens(tokens, self.path, self.diagnostics) if tokens else None, token)
        if self.check_value("выбросить"):
            token = self.advance()
            tokens = self.collect_expression_tokens()
            return ThrowStmt(parse_expr_tokens(tokens, self.path, self.diagnostics) if tokens else None, token)
        if self.check_value("прервать") or self.check_value("продолжить"):
            token = self.advance()
            self.consume_line_end()
            return BreakContinueStmt(token.value, token)
        if self.check_value("обз") or self.check_value("пер") or self.check_value("знч") or self.check_value("исп") or self.check_value("конст"):
            if self.check_value("исп") and self.is_using_expression_statement():
                token = self.advance()
                expr = parse_expr_tokens(self.collect_expression_tokens(), self.path, self.diagnostics)
                return ExprStmt(expr, token)
            return self.parse_var_decl(allow_required=False)
        if self.check_value("абстрактный") or self.check_value("статический") or self.check_value("метод"):
            return self.parse_method([])

        line_tokens = self.collect_expression_tokens()
        if not line_tokens:
            return None
        assignment_index = find_top_level_assignment(line_tokens)
        if assignment_index is not None:
            target_tokens = line_tokens[:assignment_index]
            operator = line_tokens[assignment_index].value
            value_tokens = line_tokens[assignment_index + 1 :]
            return AssignStmt(
                parse_expr_tokens(target_tokens, self.path, self.diagnostics),
                operator,
                parse_expr_tokens(value_tokens, self.path, self.diagnostics),
                line_tokens[assignment_index],
            )
        expr = parse_expr_tokens(line_tokens, self.path, self.diagnostics)
        return ExprStmt(expr, line_tokens[0])

    def parse_if(self) -> IfStmt:
        if self.check_value("if"):
            token = self.advance()
        else:
            token = self.expect_value("если", "Ожидалось ключевое слово 'если'.") or self.peek()
        condition_tokens = self.collect_expression_tokens()
        self.report_forbidden_1c8_tokens(condition_tokens, {"Тогда"})
        condition = parse_expr_tokens(condition_tokens, self.path, self.diagnostics)
        then_body = self.parse_statements_until({"иначе"})
        elifs: list[tuple[Expr, list[Stmt]]] = []
        else_body: list[Stmt] = []
        while self.match_value("иначе"):
            if self.match_value("если"):
                elif_condition = parse_expr_tokens(self.collect_expression_tokens(), self.path, self.diagnostics)
                elifs.append((elif_condition, self.parse_statements_until({"иначе"})))
            else:
                self.consume_header_tail()
                else_body = self.parse_statements_until(set())
                break
        self.expect_block_close(token, "если")
        return IfStmt(condition, then_body, elifs, else_body, token)

    def parse_choice(self) -> ChoiceStmt:
        token = self.expect_value("выбор", "Ожидалось ключевое слово 'выбор'.") or self.peek()
        header_tokens = self.collect_until_line()
        expression = parse_expr_tokens(header_tokens, self.path, self.diagnostics) if header_tokens else None
        branches: list[tuple[Expr | None, list[Stmt]]] = []
        else_body: list[Stmt] = []
        while not self.peek().end_marker:
            self.skip_newlines()
            if self.check_value(";"):
                break
            if self.match_value("когда"):
                condition_tokens = self.collect_until_line()
                condition = parse_expr_tokens(condition_tokens, self.path, self.diagnostics) if condition_tokens else None
                branches.append((condition, self.parse_statements_until({"когда", "иначе"})))
                continue
            if self.match_value("иначе"):
                self.consume_header_tail()
                else_body = self.parse_statements_until(set())
                break
            self.error(self.peek(), "XBSL0002", "В блоке 'выбор' ожидалось 'когда', 'иначе' или ';'.")
            self.skip_line()
        self.expect_block_close(token, "выбор")
        return ChoiceStmt(expression, branches, else_body, token)

    def parse_while(self) -> WhileStmt:
        token = self.expect_value("пока", "Ожидалось ключевое слово 'пока'.") or self.peek()
        condition = parse_expr_tokens(self.collect_expression_tokens(), self.path, self.diagnostics)
        body = self.parse_statements_until(set())
        self.expect_block_close(token, "пока")
        return WhileStmt(condition, body, token)

    def parse_for(self) -> ForStmt:
        token = self.expect_value("для", "Ожидалось ключевое слово 'для'.") or self.peek()
        header_tokens = self.collect_until_line()
        name = header_tokens[0].value if header_tokens and header_tokens[0].kind == "IDENT" else None
        body = self.parse_statements_until(set())
        self.expect_block_close(token, "для")
        return ForStmt(name, header_tokens, body, token)

    def parse_try(self) -> TryStmt:
        token = self.expect_value("попытка", "Ожидалось ключевое слово 'попытка'.") or self.peek()
        self.consume_header_tail()
        body = self.parse_statements_until({"поймать", "вконце"})
        catches: list[tuple[str | None, TypeRef | None, list[Stmt]]] = []
        finally_body: list[Stmt] = []
        while self.match_value("поймать"):
            name = None
            type_ref = None
            if self.check_ident():
                name_token = self.advance()
                name = name_token.value
                if self.match_value(":"):
                    type_ref = make_type_ref(self.collect_type_until_values({"\n"}), name_token)
                else:
                    self.consume_header_tail()
            else:
                self.consume_header_tail()
            catches.append((name, type_ref, self.parse_statements_until({"поймать", "вконце"})))
        if self.match_value("вконце"):
            self.consume_header_tail()
            finally_body = self.parse_statements_until(set())
        self.expect_block_close(token, "попытка")
        return TryStmt(body, catches, finally_body, token)

    def parse_block(self) -> BlockStmt:
        token = self.expect_value("область", "Ожидалось ключевое слово 'область'.") or self.peek()
        self.consume_header_tail()
        body = self.parse_statements_until(set())
        self.expect_block_close(token, "область")
        return BlockStmt(body, token)

    def expect_block_close(self, opener: Token, kind: str) -> None:
        self.skip_newlines()
        if self.match_value(";"):
            return
        self.error(opener, "XBSL0003", f"Блок '{kind}' не закрыт символом ';'.")

    def check_forbidden_1c8_construct(self) -> bool:
        return self.peek().value in FORBIDDEN_1C8 - {"Новый", "Тогда"}

    def report_forbidden_1c8_tokens(self, tokens: list[Token], values: set[str]) -> None:
        for token in tokens:
            if token.value in values:
                self.report_forbidden_1c8_construct(token)

    def report_forbidden_1c8_construct(self, token: Token) -> None:
        self.error(
            token,
            "XBSL0001",
            f"Конструкция '{token.value}' относится к синтаксису 1С:Предприятия 8 и недопустима в XBSL.",
        )

    def collect_until_line(self) -> list[Token]:
        return self.collect_until_values({"\n"})

    def collect_expression_tokens(self) -> list[Token]:
        result: list[Token] = []
        while not self.peek().end_marker:
            line = self.collect_until_line()
            if line:
                result.extend(line)
            self.skip_newlines()
            if not self.should_continue_expression(result):
                break
        return result

    def should_continue_expression(self, tokens: list[Token]) -> bool:
        if self.peek().end_marker or self.check_value(";"):
            return False
        if self.peek().value in {"иначе", "когда", "поймать", "вконце"}:
            return False
        if not tokens:
            return True
        if tokens[-1].value in {"+", "-", "*", "/", "%", "и", "или", "??", ":", ",", "=", "(", "[", "{", ".", "?."}:
            return True
        return self.peek().value in {"+", "-", "*", "/", "%", "и", "или", "??", "?", ":", ".", "?.", ","}

    def is_using_expression_statement(self) -> bool:
        return (
            self.peek().value == "исп"
            and self.current + 2 < len(self.tokens)
            and self.tokens[self.current + 1].kind == "IDENT"
            and self.tokens[self.current + 2].value in {".", "::", "("}
        )

    def collect_until_values(self, values: set[str]) -> list[Token]:
        result: list[Token] = []
        depth = 0
        while not self.peek().end_marker:
            token = self.peek()
            if depth == 0 and (token.value in values or token.value == ";"):
                break
            if depth == 0 and "\n" in values and token.kind == "NEWLINE":
                break
            if token.kind == "NEWLINE" and depth == 0:
                break
            if token.value in {"(", "[", "{"}:
                depth += 1
            elif token.value in {")", "]", "}"} and depth > 0:
                depth -= 1
            result.append(self.advance())
        self.consume_line_end()
        return result

    def collect_type_until_values(self, values: set[str]) -> list[Token]:
        result: list[Token] = []
        paren_depth = 0
        angle_depth = 0
        while not self.peek().end_marker:
            token = self.peek()
            if paren_depth == 0 and angle_depth == 0 and (token.value in values or token.value == ";"):
                break
            if paren_depth == 0 and angle_depth == 0 and "\n" in values and token.kind == "NEWLINE":
                break
            if token.kind == "NEWLINE" and paren_depth == 0 and angle_depth == 0:
                break
            if token.value in {"(", "["}:
                paren_depth += 1
            elif token.value in {")", "]"} and paren_depth > 0:
                paren_depth -= 1
            elif token.value == "<":
                angle_depth += 1
            elif token.value == ">" and angle_depth > 0:
                angle_depth -= 1
            result.append(self.advance())
        self.consume_line_end()
        return result

    def collect_default_expr_until_values(self, values: set[str]) -> list[Token]:
        result: list[Token] = []
        paren_depth = 0
        angle_depth = 0
        while not self.peek().end_marker:
            token = self.peek()
            if paren_depth == 0 and angle_depth == 0 and (token.value in values or token.value == ";"):
                break
            if token.value in {"(", "[", "{"}:
                paren_depth += 1
            elif token.value in {")", "]", "}"} and paren_depth > 0:
                paren_depth -= 1
            elif token.value == "<":
                angle_depth += 1
            elif token.value == ">" and angle_depth > 0:
                angle_depth -= 1
            result.append(self.advance())
        return result

    def consume_header_tail(self) -> None:
        while not self.peek().end_marker and self.peek().kind != "NEWLINE" and self.peek().value != ";":
            self.advance()
        self.consume_line_end()

    def consume_line_end(self) -> None:
        if self.check_newline():
            self.skip_newlines()

    def skip_line(self) -> None:
        while not self.peek().end_marker and self.peek().kind != "NEWLINE" and self.peek().value != ";":
            self.advance()
        self.consume_line_end()

    def skip_balanced(self, open_value: str, close_value: str) -> None:
        depth = 1
        while not self.peek().end_marker and depth > 0:
            token = self.advance()
            if token.value == open_value:
                depth += 1
            elif token.value == close_value:
                depth -= 1

    def expect_ident(self, message: str) -> Token | None:
        if self.check_ident():
            return self.advance()
        self.error(self.peek(), "XBSL0005", message)
        return None

    def expect_value(self, value: str, message: str) -> Token | None:
        if self.match_value(value):
            return self.previous()
        self.error(self.peek(), "XBSL0005", message)
        return None

    def error(self, token: Token, code: str, message: str) -> None:
        self.diagnostics.append(Diagnostic(self.path, token.line, token.column, "ERROR", code, message))

    def skip_newlines(self) -> None:
        while self.check_newline():
            self.advance()

    def match_value(self, value: str) -> bool:
        if self.check_value(value):
            self.advance()
            return True
        return False

    def check_value(self, value: str) -> bool:
        token = self.peek()
        return token.value == value or (value == "\n" and token.kind == "NEWLINE")

    def check_ident(self) -> bool:
        return self.peek().kind == "IDENT"

    def check_newline(self) -> bool:
        return self.peek().kind == "NEWLINE"

    def advance(self) -> Token:
        token = self.peek()
        if not token.end_marker:
            self.current += 1
        return token

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]


class ExpressionParser:
    PRECEDENCE = {
        "или": 1,
        "??": 2,
        "и": 3,
        "==": 4,
        "!=": 4,
        ">": 4,
        ">=": 4,
        "<": 4,
        "<=": 4,
        "+": 5,
        "-": 5,
        "*": 6,
        "/": 6,
        "%": 6,
        "**": 7,
    }

    def __init__(self, tokens: list[Token], path: str, diagnostics: list[Diagnostic]) -> None:
        self.tokens = tokens + [Token("EOF", "<eof>", tokens[-1].line if tokens else 1, tokens[-1].column if tokens else 1, -1)]
        self.path = path
        self.diagnostics = diagnostics
        self.current = 0

    def parse(self) -> Expr:
        if self.peek().end_marker:
            return UnknownExpr()
        expr = self.parse_expression()
        return expr

    def parse_expression(self, min_precedence: int = 0) -> Expr:
        left = self.parse_prefix()
        left = self.parse_postfix(left)

        while not self.peek().end_marker:
            if min_precedence <= 0 and self.match_value("?"):
                when_true = self.parse_expression()
                self.expect_value(":", "В тернарной операции ожидался ':'.")
                when_false = self.parse_expression()
                left = TernaryExpr(left, when_true, when_false, left.token)
                continue
            if self.check_value("это"):
                token = self.advance()
                negated = self.match_value("не")
                type_ref = make_type_ref(self.collect_type_tail(), token)
                left = TypeCheckExpr(left, type_ref, negated, token)
                continue
            if self.check_value("как"):
                token = self.advance()
                type_ref = make_type_ref(self.collect_type_tail(), token)
                left = CastExpr(left, type_ref, token)
                continue

            operator = self.peek().value
            precedence = self.PRECEDENCE.get(operator)
            if precedence is None or precedence < min_precedence:
                break
            token = self.advance()
            next_min = precedence if operator == "**" else precedence + 1
            right = self.parse_expression(next_min)
            left = BinaryExpr(left, operator, right, token)
        return left

    def parse_prefix(self) -> Expr:
        token = self.advance()
        if token.end_marker:
            return UnknownExpr(token)
        if token.kind == "NUMBER":
            return LiteralExpr("Число", token)
        if token.kind == "STRING":
            return LiteralExpr("Строка", token)
        if token.kind == "BRACED_LITERAL":
            prefix = token.value.split("{", 1)[0]
            if prefix in TYPE_LITERAL_NAMES:
                return LiteralExpr(prefix, token)
            return LiteralExpr("неизвестно", token)
        if token.value in BUILTIN_VALUES:
            return LiteralExpr(BUILTIN_VALUES[token.value], token)
        if token.value == "не":
            return UnaryExpr("не", self.parse_expression(8), token)
        if token.value == "-":
            return UnaryExpr("-", self.parse_expression(8), token)
        if token.value == "&":
            if self.peek().kind == "IDENT":
                self.advance()
            return LiteralExpr("функция", token)
        if token.value == "(":
            expr = self.parse_expression()
            self.expect_value(")", "Выражение в скобках не закрыто ')'.")
            return expr
        if token.value == "[":
            return self.parse_collection("Массив", token, "]")
        if token.value == "{":
            return self.parse_collection("Множество", token, "}")
        if token.value == "<":
            type_tokens = self.collect_type_argument_tokens()
            if self.match_value("["):
                return self.parse_collection("Массив", token, "]", type_tokens)
            if self.match_value("{"):
                return self.parse_collection("Множество", token, "}", type_tokens)
            return UnknownExpr(token)
        if token.value == "Тип" and self.match_value("<"):
            self.skip_type_arguments()
            return LiteralExpr("Тип", token)
        if token.value == "Новый":
            if self.looks_like_legacy_new_expression():
                self.error(token, "XBSL0001", f"Конструкция '{token.value}' относится к синтаксису 1С:Предприятия 8 и недопустима в XBSL.")
                type_tokens = self.collect_until_call_start()
                type_ref = make_type_ref(type_tokens, token)
                args = self.parse_argument_list() if self.check_value("(") else []
                return NewExpr(type_ref, args, token)
            return NameExpr(token.value, token)
        if token.value == "новый":
            type_tokens = self.collect_until_call_start()
            type_ref = make_type_ref(type_tokens, token)
            args = self.parse_argument_list() if self.check_value("(") else []
            return NewExpr(type_ref, args, token)
        if token.kind == "IDENT":
            return NameExpr(token.value, token)
        self.error(token, "XBSL0002", f"Неожиданный токен в выражении: '{token.value}'.")
        return UnknownExpr(token)

    def parse_postfix(self, expr: Expr) -> Expr:
        while not self.peek().end_marker:
            if self.match_value(".") or self.match_value("?.") or self.match_value("::"):
                op = self.previous()
                safe = op.value == "?."
                name = self.expect_ident("После '.' ожидалось имя свойства или метода.")
                expr = MemberExpr(expr, name.value if name else "<error>", safe, op)
                if self.check_value("("):
                    expr = CallExpr(expr, self.parse_argument_list(), op)
                continue
            if self.check_value("<") and self.looks_like_generic_call():
                self.skip_type_arguments()
                if self.check_value("("):
                    expr = CallExpr(expr, self.parse_argument_list(), expr.token)
                continue
            if self.check_value("("):
                expr = CallExpr(expr, self.parse_argument_list(), expr.token)
                continue
            if self.match_value("["):
                token = self.previous()
                index = self.parse_expression()
                self.expect_value("]", "Индексатор не закрыт ']'.")
                expr = IndexExpr(expr, index, token)
                continue
            if isinstance(expr, NameExpr) and expr.name in TYPE_LITERAL_NAMES and self.match_value("{"):
                self.skip_balanced("{", "}")
                expr = LiteralExpr(expr.name, expr.token)
                continue
            break
        return expr

    def parse_collection(self, kind: str, token: Token, close_value: str, type_tokens: list[Token] | None = None) -> CollectionExpr:
        groups = self.collect_argument_groups(close_value)
        elements = [
            parse_expr_tokens(group, self.path, self.diagnostics)
            for group in groups
            if group and not all(token.value == ":" for token in group)
        ]
        self.expect_value(close_value, f"Коллекционный литерал не закрыт '{close_value}'.")
        if close_value == "}" and any(any(token.value == ":" for token in group) for group in groups):
            kind = "Соответствие"
        return CollectionExpr(kind, elements, token, collection_type_ref(kind, token, type_tokens or []))

    def parse_argument_list(self) -> list[Arg]:
        open_token = self.expect_value("(", "Ожидался список аргументов.")
        groups = self.collect_argument_groups(")")
        self.expect_value(")", "Список аргументов не закрыт ')'.")
        args: list[Arg] = []
        for group in groups:
            if not group:
                continue
            name = None
            value_tokens = group
            if len(group) >= 3 and group[0].kind == "IDENT" and group[1].value == "=":
                name = group[0].value
                value_tokens = group[2:]
            args.append(Arg(name, parse_expr_tokens(value_tokens, self.path, self.diagnostics), group[0]))
        if not groups and open_token:
            return []
        return args

    def collect_argument_groups(self, close_value: str) -> list[list[Token]]:
        groups: list[list[Token]] = []
        current: list[Token] = []
        depth = 0
        angle_depth = 0
        while not self.peek().end_marker:
            token = self.peek()
            if depth == 0 and angle_depth == 0 and token.value == close_value:
                break
            if depth == 0 and angle_depth == 0 and token.value == ",":
                groups.append(current)
                current = []
                self.advance()
                continue
            if token.value in {"(", "[", "{"}:
                depth += 1
            elif token.value in {")", "]", "}"} and depth > 0:
                depth -= 1
            elif token.value == "<":
                angle_depth += 1
            elif token.value == ">" and angle_depth > 0:
                angle_depth -= 1
            current.append(self.advance())
        if current:
            groups.append(current)
        return groups

    def collect_type_tail(self) -> list[Token]:
        result: list[Token] = []
        depth = 0
        while not self.peek().end_marker:
            token = self.peek()
            if depth == 0 and token.value == "?":
                previous = result[-1] if result else None
                if previous is None or previous.index + len(previous.value) != token.index:
                    break
            if depth == 0 and token.value in {"и", "или", ":", ")", "]", "}"}:
                break
            if token.value in {"<", "(", "["}:
                depth += 1
            elif token.value in {">", ")", "]"} and depth > 0:
                depth -= 1
            result.append(self.advance())
        return result

    def collect_until_call_start(self) -> list[Token]:
        result: list[Token] = []
        depth = 0
        while not self.peek().end_marker:
            token = self.peek()
            if depth == 0 and token.value == "(":
                break
            if token.value == "<":
                depth += 1
            elif token.value == ">" and depth > 0:
                depth -= 1
            result.append(self.advance())
        return result

    def skip_type_arguments(self) -> None:
        depth = 1
        while not self.peek().end_marker and depth > 0:
            token = self.advance()
            if token.value == "<":
                depth += 1
            elif token.value == ">":
                depth -= 1
                if depth == 0:
                    return

    def collect_type_argument_tokens(self) -> list[Token]:
        result: list[Token] = []
        depth = 1
        while not self.peek().end_marker and depth > 0:
            token = self.advance()
            if token.value == "<":
                depth += 1
            elif token.value == ">":
                depth -= 1
                if depth == 0:
                    return result
            result.append(token)
        return result

    def looks_like_generic_call(self) -> bool:
        depth = 0
        position = self.current
        while position < len(self.tokens):
            token = self.tokens[position]
            if token.value == "<":
                depth += 1
            elif token.value == ">":
                depth -= 1
                if depth == 0:
                    return position + 1 < len(self.tokens) and self.tokens[position + 1].value == "("
            elif token.end_marker:
                return False
            position += 1
        return False

    def looks_like_legacy_new_expression(self) -> bool:
        next_token = self.peek()
        return next_token.kind in {"IDENT", "BRACED_LITERAL"} or next_token.value == "<"

    def skip_balanced(self, open_value: str, close_value: str) -> None:
        depth = 1
        while not self.peek().end_marker and depth > 0:
            token = self.advance()
            if token.value == open_value:
                depth += 1
            elif token.value == close_value:
                depth -= 1

    def expect_ident(self, message: str) -> Token | None:
        if self.peek().kind == "IDENT":
            return self.advance()
        self.error(self.peek(), "XBSL0002", message)
        return None

    def expect_value(self, value: str, message: str) -> Token | None:
        if self.match_value(value):
            return self.previous()
        self.error(self.peek(), "XBSL0002", message)
        return None

    def match_value(self, value: str) -> bool:
        if self.check_value(value):
            self.advance()
            return True
        return False

    def check_value(self, value: str) -> bool:
        return self.peek().value == value

    def advance(self) -> Token:
        token = self.peek()
        if not token.end_marker:
            self.current += 1
        return token

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def peek(self) -> Token:
        return self.tokens[self.current]

    def error(self, token: Token, code: str, message: str) -> None:
        self.diagnostics.append(Diagnostic(self.path, token.line, token.column, "ERROR", code, message))


def parse_expr_tokens(tokens: list[Token], path: str, diagnostics: list[Diagnostic]) -> Expr:
    tokens = [token for token in tokens if token.kind != "NEWLINE"]
    if not tokens:
        return UnknownExpr()
    arrow_index = top_level_arrow_index(tokens)
    if arrow_index is not None:
        params = parse_lambda_params(tokens[:arrow_index])
        return_expr = parse_expr_tokens(tokens[arrow_index + 1 :], path, diagnostics) if arrow_index + 1 < len(tokens) else None
        return LambdaExpr(params, [], return_expr, tokens[0])
    return ExpressionParser(tokens, path, diagnostics).parse()


def is_block_lambda_header(tokens: list[Token]) -> bool:
    arrow_index = top_level_arrow_index(tokens)
    return arrow_index is not None and arrow_index == len(tokens) - 1


def top_level_arrow_index(tokens: list[Token]) -> int | None:
    depth = 0
    for index, token in enumerate(tokens):
        if token.value in {"(", "[", "{"}:
            depth += 1
        elif token.value in {")", "]", "}"} and depth > 0:
            depth -= 1
        elif depth == 0 and token.value == "->":
            return index
    return None


def parse_lambda_params(tokens: list[Token]) -> list[Param]:
    tokens = [token for token in tokens if token.kind != "NEWLINE"]
    if tokens and tokens[0].value == "метод":
        tokens = tokens[1:]
    if tokens and tokens[0].value == "(" and tokens[-1].value == ")":
        tokens = tokens[1:-1]
    if not tokens:
        return []
    groups = split_token_groups(tokens, ",")
    params: list[Param] = []
    for group in groups:
        if not group:
            continue
        name_token = next((token for token in group if token.kind == "IDENT"), group[0])
        colon_index = next((index for index, token in enumerate(group) if token.value == ":"), None)
        if colon_index is None:
            type_ref = TypeRef("неизвестно", name_token, ("неизвестно",))
        else:
            type_ref = make_type_ref(group[colon_index + 1 :], name_token)
        params.append(Param(name_token.value, type_ref, None, name_token))
    return params


def split_token_groups(tokens: list[Token], separator: str) -> list[list[Token]]:
    groups: list[list[Token]] = []
    current: list[Token] = []
    depth = 0
    for token in tokens:
        if token.value in {"(", "[", "{", "<"}:
            depth += 1
        elif token.value in {")", "]", "}", ">"} and depth > 0:
            depth -= 1
        if token.value == separator and depth == 0:
            groups.append(current)
            current = []
        else:
            current.append(token)
    groups.append(current)
    return groups


def make_type_ref(tokens: list[Token], fallback_token: Token) -> TypeRef:
    if not tokens:
        return TypeRef("", fallback_token)
    text = type_tokens_text(tokens)
    identifiers: list[str] = []
    dotted = False
    for index, token in enumerate(tokens):
        if token.kind != "IDENT":
            continue
        previous_is_dot = index > 0 and tokens[index - 1].value in {".", "::"}
        next_is_dot = index + 1 < len(tokens) and tokens[index + 1].value in {".", "::"}
        if previous_is_dot or next_is_dot:
            dotted = True
        identifiers.append(token.value)
    return TypeRef(text, tokens[0], tuple(identifiers), "Неопределено" in identifiers, dotted)


def type_tokens_text(tokens: list[Token]) -> str:
    parts: list[str] = []
    previous = ""
    for token in tokens:
        value = token.value
        if value == "\n":
            continue
        if parts and value not in {">", "<", "|", "?", ",", ")", "]", ".", "::"} and previous not in {"<", "|", "(", "[", ",", ".", "::"}:
            parts.append(" ")
        parts.append(value)
        previous = value
    return "".join(parts).strip()


def split_union_type(text: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char == "<":
            depth += 1
        elif char == ">" and depth > 0:
            depth -= 1
        if char == "|" and depth == 0:
            result.append("".join(current))
            current = []
        else:
            current.append(char)
    result.append("".join(current))
    return result


def base_type_name(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None
    if "." in text:
        return text.rsplit(".", 1)[-1].split("<", 1)[0].strip()
    return text.split("<", 1)[0].strip()


def collection_type_ref(kind: str, token: Token, type_tokens: list[Token]) -> TypeRef | None:
    if not type_tokens:
        return None
    type_args = type_tokens_text(type_tokens)
    identifiers = tuple(token.value for token in type_tokens if token.kind == "IDENT")
    return TypeRef(f"{kind}<{type_args}>", token, identifiers, "Неопределено" in identifiers)


def array_element_type_ref(type_ref: TypeRef | None) -> TypeRef | None:
    if type_ref is None:
        return None
    for part in split_union_type(type_ref.text):
        if base_type_name(part) != "Массив":
            continue
        args = generic_argument_texts(part)
        if args:
            return TypeRef(args[0], type_ref.token, (), "Неопределено" in args[0])
    return None


def generic_argument_texts(type_text: str) -> list[str]:
    start = type_text.find("<")
    if start < 0:
        return []
    args: list[str] = []
    current: list[str] = []
    depth = 0
    for char in type_text[start + 1 :]:
        if char == "<":
            depth += 1
            current.append(char)
        elif char == ">" and depth > 0:
            depth -= 1
            current.append(char)
        elif char == ">" and depth == 0:
            args.append("".join(current).strip())
            return args
        elif char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    return []


def find_top_level_assignment(tokens: list[Token]) -> int | None:
    depth = 0
    for index, token in enumerate(tokens):
        if token.value in {"(", "[", "{"}:
            depth += 1
        elif token.value in {")", "]", "}"} and depth > 0:
            depth -= 1
        elif depth == 0 and token.value in ASSIGNMENT_OPERATORS:
            if token.value == "=" and index > 0 and tokens[index - 1].value in {">", "<", "!", "="}:
                continue
            return index
    return None


@dataclass
class Symbol:
    name: str
    kind: str
    type_value: XbslType
    mutable: bool
    token: Token
    type_ref: TypeRef | None = None


class Scope:
    def __init__(self, parent: "Scope | None" = None) -> None:
        self.parent = parent
        self.symbols: dict[str, Symbol] = {}

    def lookup(self, name: str) -> Symbol | None:
        if name in self.symbols:
            return self.symbols[name]
        return self.parent.lookup(name) if self.parent else None

    def local(self, name: str) -> Symbol | None:
        return self.symbols.get(name)

    def declare(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True


@dataclass
class MethodSig:
    name: str
    params: list[Param]
    return_type: TypeRef | None
    token: Token
    annotations: tuple[str, ...]


class SemanticAnalyzer:
    def __init__(
        self,
        modules: list[Module],
        diagnostics: list[Diagnostic],
        external_types: Iterable[str] = (),
        external_symbols: Iterable[str] = (),
    ) -> None:
        self.modules = modules
        self.diagnostics = diagnostics
        self.declared_types: set[str] = set(BUILTIN_TYPES) | set(external_types)
        self.external_symbols: set[str] = set(external_symbols)
        self.project_context = bool(self.external_symbols)
        self.methods: dict[str, list[MethodSig]] = {}
        self.methods_by_module: dict[str, dict[str, list[MethodSig]]] = {}
        self.current_return_type: XbslType = XbslType.nothing()
        self.current_path = "<unknown>"

    def analyze(self) -> None:
        self.collect_declarations()
        for module in self.modules:
            self.current_path = module.path
            scope = Scope()
            self.add_module_symbols(scope, module)
            for declaration in module.declarations:
                self.analyze_declaration(declaration, scope)

    def collect_declarations(self) -> None:
        for module in self.modules:
            for declaration in module.declarations:
                if isinstance(declaration, TypeDecl):
                    self.declared_types.add(declaration.name)
                    for member in declaration.members:
                        if isinstance(member, MethodDecl):
                            self.add_method_sig(module.path, member)
                elif isinstance(declaration, EnumDecl):
                    self.declared_types.add(declaration.name)
                elif isinstance(declaration, MethodDecl):
                    self.add_method_sig(module.path, declaration)

    def add_method_sig(self, module_path: str, method: MethodDecl) -> None:
        self.methods.setdefault(method.name, []).append(MethodSig(method.name, method.params, method.return_type, method.token, method.annotations))
        self.methods_by_module.setdefault(module_path, {}).setdefault(method.name, []).append(
            MethodSig(method.name, method.params, method.return_type, method.token, method.annotations)
        )

    def add_module_symbols(self, scope: Scope, module: Module) -> None:
        for declaration in module.declarations:
            if isinstance(declaration, VarDecl):
                type_value = self.type_of_decl(declaration)
                scope.declare(Symbol(declaration.name, "variable", type_value, declaration.kind == "пер", declaration.token, self.type_ref_of_decl(declaration)))

    def analyze_declaration(self, declaration: Decl, scope: Scope) -> None:
        if isinstance(declaration, VarDecl):
            self.check_var_decl(declaration, scope)
        elif isinstance(declaration, MethodDecl):
            self.check_method(declaration, scope)
        elif isinstance(declaration, TypeDecl):
            for member in declaration.members:
                if isinstance(member, VarDecl):
                    if declaration.kind == "структура" and member.name == "Тип":
                        self.add_error(member.token, "XBSL0005", 'Недопустимое имя поля "Тип".')
                    self.check_type_ref(member.type_ref)
                elif isinstance(member, MethodDecl):
                    self.check_method(member, scope)
        elif isinstance(declaration, EnumDecl):
            pass

    def check_method(self, method: MethodDecl, outer_scope: Scope) -> None:
        for param in method.params:
            self.check_type_ref(param.type_ref)
        self.check_type_ref(method.return_type)

        previous_return = self.current_return_type
        self.current_return_type = method.return_type.to_type() if method.return_type else XbslType.nothing()
        method_scope = Scope(outer_scope)
        if not method.static:
            self.declare(method_scope, Symbol("этот", "context", XbslType.unknown(), False, method.token))
        for param in method.params:
            self.declare(method_scope, Symbol(param.name, "parameter", param.type_ref.to_type(), True, param.token, param.type_ref))
        for statement in method.body:
            self.check_statement(statement, method_scope)
        self.current_return_type = previous_return

    def check_statement(self, statement: Stmt, scope: Scope) -> None:
        if isinstance(statement, VarDecl):
            self.check_var_decl(statement, scope)
        elif isinstance(statement, MethodDecl):
            self.check_method(statement, scope)
        elif isinstance(statement, IfStmt):
            self.require_type(self.infer_expr(statement.condition, scope), XbslType({"Булево"}), statement.condition.token, "Условие 'если' должно иметь тип Булево.", "XBSL0014")
            self.check_child_block(statement.then_body, scope)
            for condition, body in statement.elifs:
                self.require_type(self.infer_expr(condition, scope), XbslType({"Булево"}), condition.token, "Условие 'иначе если' должно иметь тип Булево.", "XBSL0014")
                self.check_child_block(body, scope)
            if statement.else_body:
                self.check_child_block(statement.else_body, scope)
        elif isinstance(statement, WhileStmt):
            self.require_type(self.infer_expr(statement.condition, scope), XbslType({"Булево"}), statement.condition.token, "Условие 'пока' должно иметь тип Булево.", "XBSL0014")
            self.check_child_block(statement.body, scope)
        elif isinstance(statement, ForStmt):
            child = Scope(scope)
            if statement.name:
                is_counter = any(token.value == "по" for token in statement.header_tokens)
                self.declare(child, Symbol(statement.name, "variable", XbslType({"Число"}) if is_counter else XbslType.unknown(), False, statement.token))
            self.check_statements(statement.body, child)
        elif isinstance(statement, ChoiceStmt):
            if statement.expression is not None:
                self.infer_expr(statement.expression, scope)
            for condition, body in statement.branches:
                child = Scope(scope)
                if condition is not None:
                    self.infer_expr(condition, child)
                self.check_statements(body, child)
            if statement.else_body:
                self.check_child_block(statement.else_body, scope)
        elif isinstance(statement, TryStmt):
            self.check_child_block(statement.body, scope)
            for name, type_ref, body in statement.catches:
                self.check_type_ref(type_ref)
                child = Scope(scope)
                if name:
                    self.declare(child, Symbol(name, "variable", type_ref.to_type() if type_ref else XbslType({"Исключение"}), False, statement.token, type_ref))
                self.check_statements(body, child)
            if statement.finally_body:
                self.check_child_block(statement.finally_body, scope)
        elif isinstance(statement, BlockStmt):
            self.check_child_block(statement.body, scope)
        elif isinstance(statement, ReturnStmt):
            self.check_return(statement, scope)
        elif isinstance(statement, ThrowStmt):
            if statement.value is not None:
                self.infer_expr(statement.value, scope)
        elif isinstance(statement, AssignStmt):
            self.check_assignment(statement, scope)
        elif isinstance(statement, ExprStmt):
            self.infer_expr(statement.expr, scope)
        elif isinstance(statement, BreakContinueStmt):
            pass

    def check_statements(self, statements: list[Stmt], scope: Scope) -> None:
        for statement in statements:
            self.check_statement(statement, scope)

    def check_child_block(self, statements: list[Stmt], parent: Scope) -> None:
        self.check_statements(statements, Scope(parent))

    def check_var_decl(self, declaration: VarDecl, scope: Scope) -> None:
        self.check_type_ref(declaration.type_ref)
        initializer_type = self.infer_expr(declaration.initializer, scope) if declaration.initializer is not None else None
        declared_type = declaration.type_ref.to_type() if declaration.type_ref else (initializer_type or XbslType.unknown())
        if declaration.type_ref is not None and initializer_type is not None:
            self.require_type(initializer_type, declared_type, declaration.token, f"Значение типа {initializer_type.display()} нельзя присвоить переменной '{declaration.name}' типа {declared_type.display()}.", "XBSL0009")
        existing = scope.local(declaration.name)
        if existing is not None and existing.token is declaration.token:
            return
        self.declare(scope, Symbol(declaration.name, "variable", declared_type, declaration.kind == "пер", declaration.token, self.type_ref_of_decl(declaration)))

    def check_assignment(self, statement: AssignStmt, scope: Scope) -> None:
        if contains_safe_member(statement.target):
            self.add_error(statement.token, "XBSL0012", "Оператор '?.' нельзя использовать слева от присваивания.")
        target_type = self.assignment_target_type(statement.target, scope)
        value_type = self.infer_expr(statement.value, scope)
        if target_type is not None:
            self.require_type(value_type, target_type, statement.token, f"Значение типа {value_type.display()} нельзя присвоить цели типа {target_type.display()}.", "XBSL0009")

    def assignment_target_type(self, expr: Expr, scope: Scope) -> XbslType | None:
        if isinstance(expr, NameExpr):
            symbol = scope.lookup(expr.name)
            if symbol is None:
                if self.project_context:
                    return XbslType.unknown()
                self.add_error(expr.token, "XBSL0007", f"Имя '{expr.name}' не объявлено в доступной области видимости.")
                return None
            if not symbol.mutable:
                self.add_error(expr.token, "XBSL0011", f"Нельзя присваивать новое значение '{expr.name}': переменная объявлена как {symbol.kind if symbol.kind != 'variable' else 'знч/исп'} или только для чтения.")
            return symbol.type_value
        if isinstance(expr, MemberExpr):
            self.infer_expr(expr.obj, scope)
            return XbslType.unknown()
        if isinstance(expr, IndexExpr):
            self.infer_expr(expr.obj, scope)
            self.infer_expr(expr.index, scope)
            return XbslType.unknown()
        self.add_error(expr.token, "XBSL0012", "Слева от присваивания должна быть переменная, свойство или индексатор.")
        return None

    def check_return(self, statement: ReturnStmt, scope: Scope) -> None:
        if statement.value is None:
            value_type = XbslType.nothing()
        else:
            value_type = self.infer_expr(statement.value, scope)
        if self.current_return_type.names == frozenset({"ничто"}) and statement.value is not None:
            self.add_error(statement.token, "XBSL0009", "Метод без результата не должен возвращать значение.")
            return
        if self.current_return_type.names != frozenset({"ничто"}):
            self.require_type(value_type, self.current_return_type, statement.token, f"Метод должен возвращать {self.current_return_type.display()}, но возвращается {value_type.display()}.", "XBSL0009")

    def infer_expr(self, expr: Expr | None, scope: Scope) -> XbslType:
        if expr is None or isinstance(expr, UnknownExpr):
            return XbslType.unknown()
        if isinstance(expr, LiteralExpr):
            return XbslType({expr.type_name})
        if isinstance(expr, NameExpr):
            if expr.name in BUILTIN_VALUES:
                return XbslType({BUILTIN_VALUES[expr.name]})
            if expr.name in self.declared_types:
                return XbslType.unknown()
            if expr.name in self.external_symbols:
                return XbslType.unknown()
            symbol = scope.lookup(expr.name)
            if symbol is None:
                if self.project_context:
                    return XbslType.unknown()
                self.add_error(expr.token, "XBSL0007", f"Имя '{expr.name}' не объявлено в доступной области видимости.")
                return XbslType.unknown()
            return symbol.type_value
        if isinstance(expr, UnaryExpr):
            operand_type = self.infer_expr(expr.operand, scope)
            if expr.operator == "не":
                self.require_type(operand_type, XbslType({"Булево"}), expr.token, "Оператор 'не' применим только к Булево.", "XBSL0009")
                return XbslType({"Булево"})
            if expr.operator == "-":
                self.require_type(operand_type, XbslType({"Число"}), expr.token, "Унарный '-' применим только к Число.", "XBSL0009")
                return XbslType({"Число"})
            return XbslType.unknown()
        if isinstance(expr, BinaryExpr):
            return self.infer_binary(expr, scope)
        if isinstance(expr, TernaryExpr):
            self.require_type(self.infer_expr(expr.condition, scope), XbslType({"Булево"}), expr.token, "Условие тернарной операции должно иметь тип Булево.", "XBSL0014")
            left = self.infer_expr(expr.when_true, scope)
            right = self.infer_expr(expr.when_false, scope)
            return merge_types(left, right)
        if isinstance(expr, MemberExpr):
            if not isinstance(expr.obj, NameExpr) or scope.lookup(expr.obj.name) is not None:
                self.infer_expr(expr.obj, scope)
            return XbslType.unknown()
        if isinstance(expr, IndexExpr):
            self.infer_expr(expr.obj, scope)
            self.infer_expr(expr.index, scope)
            return XbslType.unknown()
        if isinstance(expr, CallExpr):
            return self.infer_call(expr, scope)
        if isinstance(expr, NewExpr):
            self.check_type_ref(expr.type_ref)
            for arg in expr.args:
                self.infer_expr(arg.value, scope)
            return expr.type_ref.to_type()
        if isinstance(expr, TypeCheckExpr):
            self.infer_expr(expr.value, scope)
            self.check_type_ref(expr.type_ref)
            return XbslType({"Булево"})
        if isinstance(expr, CastExpr):
            self.infer_expr(expr.value, scope)
            self.check_type_ref(expr.type_ref)
            return expr.type_ref.to_type()
        if isinstance(expr, CollectionExpr):
            for element in expr.elements:
                self.infer_expr(element, scope)
            return XbslType({expr.kind})
        if isinstance(expr, LambdaExpr):
            child = Scope(scope)
            for param in expr.params:
                self.check_type_ref(param.type_ref)
                self.declare(child, Symbol(param.name, "parameter", param.type_ref.to_type(), True, param.token, param.type_ref))
            if expr.return_expr is not None:
                self.infer_expr(expr.return_expr, child)
            if expr.body:
                self.check_statements(expr.body, child)
            return XbslType({"функция"})
        return XbslType.unknown()

    def infer_binary(self, expr: BinaryExpr, scope: Scope) -> XbslType:
        left = self.infer_expr(expr.left, scope)
        right = self.infer_expr(expr.right, scope)
        if expr.operator in {"и", "или"}:
            self.require_type(left, XbslType({"Булево"}), expr.token, f"Оператор '{expr.operator}' применим только к Булево.", "XBSL0009")
            self.require_type(right, XbslType({"Булево"}), expr.token, f"Оператор '{expr.operator}' применим только к Булево.", "XBSL0009")
            return XbslType({"Булево"})
        if expr.operator in {"==", "!=", ">", ">=", "<", "<="}:
            return XbslType({"Булево"})
        if expr.operator == "??":
            return merge_types(without_undefined(left), right)
        if expr.operator == "+" and (has_type(left, "Строка") or has_type(right, "Строка")):
            return XbslType({"Строка"})
        if expr.operator in {"+", "-", "*", "/", "%", "**"}:
            self.require_type(left, XbslType({"Число"}), expr.token, f"Оператор '{expr.operator}' применим к числам.", "XBSL0009")
            self.require_type(right, XbslType({"Число"}), expr.token, f"Оператор '{expr.operator}' применим к числам.", "XBSL0009")
            return XbslType({"Число"})
        return XbslType.unknown()

    def infer_call(self, expr: CallExpr, scope: Scope) -> XbslType:
        arg_types = [self.infer_expr(arg.value, scope) for arg in expr.args]
        if isinstance(expr.callee, NameExpr):
            signatures = self.methods_by_module.get(self.current_path, {}).get(expr.callee.name)
            if not signatures:
                return XbslType.unknown()
            signature = self.match_signature(expr, signatures)
            if signature is None:
                self.add_error(expr.token, "XBSL0010", f"Вызов метода '{expr.callee.name}' не соответствует ни одной локальной сигнатуре.")
                return XbslType.unknown()
            self.check_call_argument_types(expr, signature, scope)
            return signature.return_type.to_type() if signature.return_type else XbslType.nothing()
        if isinstance(expr.callee, MemberExpr):
            self.check_array_remove_call(expr, expr.callee, arg_types, scope)
        self.infer_expr(expr.callee, scope)
        return XbslType.unknown()

    def check_array_remove_call(self, call: CallExpr, callee: MemberExpr, arg_types: list[XbslType], scope: Scope) -> None:
        if callee.name != "Удалить" or not call.args:
            return
        element_type_ref = array_element_type_ref(self.expr_type_ref(callee.obj, scope))
        if element_type_ref is None:
            return
        element_arg = next(
            ((arg, arg_types[index]) for index, arg in enumerate(call.args) if arg.name == "Элемент"),
            (call.args[0], arg_types[0]) if call.args[0].name is None else None,
        )
        if element_arg is None:
            return
        arg, arg_type = element_arg
        self.require_type(
            arg_type,
            element_type_ref.to_type(),
            arg.token,
            f"Массив.Удалить() принимает элемент типа {element_type_ref.to_type().display()}, а не индекс.",
            "XBSL0009",
        )

    def expr_type_ref(self, expr: Expr | None, scope: Scope) -> TypeRef | None:
        if expr is None:
            return None
        if isinstance(expr, NameExpr):
            symbol = scope.lookup(expr.name)
            return symbol.type_ref if symbol else None
        if isinstance(expr, CastExpr):
            return expr.type_ref
        if isinstance(expr, NewExpr):
            return expr.type_ref
        if isinstance(expr, CollectionExpr):
            return expr.type_ref
        return None

    def match_signature(self, call: CallExpr, signatures: list[MethodSig]) -> MethodSig | None:
        for signature in signatures:
            if call_matches_signature(call, signature):
                return signature
        return None

    def check_call_argument_types(self, call: CallExpr, signature: MethodSig, scope: Scope) -> None:
        positional_index = 0
        params_by_name = {param.name: param for param in signature.params}
        seen_named = False
        for arg in call.args:
            if arg.name is not None:
                seen_named = True
                param = params_by_name.get(arg.name)
            else:
                if seen_named:
                    self.add_error(arg.token, "XBSL0010", "После именованного аргумента все последующие аргументы должны быть именованными.")
                    continue
                param = signature.params[positional_index] if positional_index < len(signature.params) else None
                positional_index += 1
            if param is None:
                continue
            self.require_type(self.infer_expr(arg.value, scope), param.type_ref.to_type(), arg.token, f"Аргумент '{param.name}' ожидает {param.type_ref.to_type().display()}.", "XBSL0009")

    def check_type_ref(self, type_ref: TypeRef | None) -> None:
        if type_ref is None:
            return
        if type_ref.has_invalid_undefined:
            if not self.project_context:
                self.add_error(type_ref.token, "XBSL0013", "В составном типе используйте '?' вместо явного 'Неопределено'.")
        skip_next_dotted = False
        for index, identifier in enumerate(type_ref.identifiers):
            if skip_next_dotted:
                skip_next_dotted = False
                continue
            if identifier in BUILTIN_TYPES or identifier in self.declared_types:
                continue
            if "." in type_ref.text:
                continue
            if self.external_symbols:
                continue
            if index + 1 < len(type_ref.identifiers) and type_ref.identifiers[index + 1] == identifier:
                skip_next_dotted = True
            self.add_error(type_ref.token, "XBSL0008", f"Тип '{identifier}' не найден среди встроенных или объявленных типов.")

    def type_of_decl(self, declaration: VarDecl) -> XbslType:
        if declaration.type_ref is not None:
            return declaration.type_ref.to_type()
        if declaration.initializer is not None:
            return XbslType.unknown()
        return XbslType.unknown()

    def type_ref_of_decl(self, declaration: VarDecl) -> TypeRef | None:
        return declaration.type_ref or self.expr_type_ref(declaration.initializer, Scope())

    def declare(self, scope: Scope, symbol: Symbol) -> None:
        if not scope.declare(symbol):
            self.add_error(symbol.token, "XBSL0006", f"Имя '{symbol.name}' уже объявлено в этой области видимости.")

    def require_type(self, actual: XbslType, expected: XbslType, token: Token, message: str, code: str) -> None:
        if self.project_context and code == "XBSL0009":
            return
        if not is_assignable(expected, actual):
            self.add_error(token, code, message)

    def add_error(self, token: Token, code: str, message: str) -> None:
        self.diagnostics.append(Diagnostic(self.current_path, token.line, token.column, "ERROR", code, message))


def call_matches_signature(call: CallExpr, signature: MethodSig) -> bool:
    params = signature.params
    required = [param for param in params if param.default is None]
    if len(call.args) < len(required) or len(call.args) > len(params):
        return False
    named_started = False
    consumed_positional = 0
    used: set[str] = set()
    params_by_name = {param.name: param for param in params}
    for arg in call.args:
        if arg.name is None:
            if named_started or consumed_positional >= len(params):
                return False
            used.add(params[consumed_positional].name)
            consumed_positional += 1
            continue
        named_started = True
        if arg.name not in params_by_name or arg.name in used:
            return False
        used.add(arg.name)
    return all(param.default is not None or param.name in used for param in params)


def contains_safe_member(expr: Expr) -> bool:
    if isinstance(expr, MemberExpr):
        return expr.safe or contains_safe_member(expr.obj)
    if isinstance(expr, IndexExpr):
        return contains_safe_member(expr.obj)
    if isinstance(expr, CallExpr):
        return contains_safe_member(expr.callee)
    return False


def merge_types(left: XbslType, right: XbslType) -> XbslType:
    if left.unknown or right.unknown:
        return XbslType.unknown()
    return XbslType(set(left.names) | set(right.names))


def without_undefined(value: XbslType) -> XbslType:
    if value.unknown:
        return value
    return XbslType(set(value.names) - {"Неопределено"})


def has_type(value: XbslType, name: str) -> bool:
    return value.unknown or name in value.names


def is_assignable(expected: XbslType, actual: XbslType) -> bool:
    if expected.unknown or actual.unknown:
        return True
    if "неизвестно" in expected.names or "неизвестно" in actual.names:
        return True
    if "Объект" in expected.names and actual.names != frozenset({"Неопределено"}):
        return True
    if "ничто" in expected.names:
        return "ничто" in actual.names
    return actual.names.issubset(expected.names)


def lint_text(text: str, path: str) -> list[Diagnostic]:
    lexer = Lexer(text, path)
    tokens, diagnostics = lexer.tokenize()
    parser = Parser(tokens, path, diagnostics)
    module = parser.parse()
    analyzer = SemanticAnalyzer([module], diagnostics)
    analyzer.analyze()
    return sorted(diagnostics, key=lambda item: (item.path, item.line, item.column, item.code, item.message))


def lint_sources(
    sources: list[tuple[str, str]],
    external_types: Iterable[str] = (),
    external_symbols: Iterable[str] = (),
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    modules: list[Module] = []
    for path, text in sources:
        lexer = Lexer(text, path)
        tokens, lexer_diagnostics = lexer.tokenize()
        diagnostics.extend(lexer_diagnostics)
        parser = Parser(tokens, path, diagnostics)
        modules.append(parser.parse())
    analyzer = SemanticAnalyzer(modules, diagnostics, external_types=external_types, external_symbols=external_symbols)
    analyzer.analyze()
    if set(external_symbols):
        diagnostics = [diag for diag in diagnostics if diag.code not in PROJECT_CONTEXT_SUPPRESSED_CODES]
    return sorted(diagnostics, key=lambda item: (item.path, item.line, item.column, item.code, item.message))


def discover_files(paths: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []
    for raw_path in paths:
        if raw_path == "-":
            continue
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"Path does not exist: {path}")
        elif path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(child for child in path.rglob("*") if child.is_file() and child.suffix.lower() == ".xbsl"))
        else:
            errors.append(f"Unsupported path: {path}")
    return files, errors


def read_sources(args: argparse.Namespace) -> tuple[list[tuple[str, str]], list[str], set[str], set[str]]:
    files, errors = discover_files(args.paths)
    sources: list[tuple[str, str]] = []
    if "-" in args.paths:
        sources.append((args.stdin_name, sys.stdin.read()))
    for path in files:
        try:
            sources.append((str(path), path.read_text(encoding="utf-8")))
        except OSError as exc:
            errors.append(f"Cannot read {path}: {exc}")
        except UnicodeDecodeError as exc:
            errors.append(f"Cannot decode {path} as UTF-8: {exc}")
    if not sources and not errors:
        errors.append("No XBSL files found.")
    external_types, external_symbols = discover_project_symbols(files)
    return sources, errors, external_types, external_symbols


def discover_project_symbols(files: list[Path]) -> tuple[set[str], set[str]]:
    roots = {project_root_for(path) for path in files}
    roots = {root for root in roots if root is not None}
    types: set[str] = set()
    symbols: set[str] = set()
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".xbsl", ".yaml", ".yml"}:
                stem = path.stem.split(".", 1)[0]
                if stem:
                    symbols.add(stem)
                    types.add(stem)
            if path.suffix.lower() in {".yaml", ".yml"}:
                try:
                    for line in path.read_text(encoding="utf-8").splitlines():
                        stripped = line.strip()
                        if stripped.startswith("Имя:"):
                            name = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                            if name:
                                symbols.add(name)
                                types.add(name)
                        elif stripped.startswith("Тип:"):
                            name = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                            name = name.split("<", 1)[0].split(".", 1)[0]
                            if name:
                                types.add(name)
                except (OSError, UnicodeDecodeError):
                    continue
    return types, symbols


def project_root_for(path: Path) -> Path | None:
    current = path.parent if path.is_file() else path
    for candidate in [current, *current.parents]:
        if (candidate / "Проект.xbsl").exists() or (candidate / "Проект.yaml").exists():
            return candidate
        if candidate.name == "data" or candidate == candidate.parent:
            break
    return None


def render_text(diagnostics: list[Diagnostic]) -> str:
    return "\n".join(
        f"{diag.path}:{diag.line}:{diag.column}: {diag.severity} {diag.code} {diag.message}"
        for diag in diagnostics
    )


def render_json(diagnostics: list[Diagnostic]) -> str:
    payload = {
        "ok": not diagnostics,
        "summary": {
            "errors": sum(1 for diag in diagnostics if diag.severity == "ERROR"),
            "warnings": sum(1 for diag in diagnostics if diag.severity == "WARNING"),
        },
        "diagnostics": [diag.to_json() for diag in diagnostics],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate 1C:Element XBSL source files.")
    parser.add_argument("paths", nargs="+", help="XBSL files/directories, or '-' for stdin")
    parser.add_argument("--stdin-name", default="<stdin>", help="Diagnostic path used when reading from stdin")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    sources, errors, external_types, external_symbols = read_sources(args)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    diagnostics = lint_sources(sources, external_types=external_types, external_symbols=external_symbols)
    output = render_json(diagnostics) if args.format == "json" else render_text(diagnostics)
    if output:
        print(output)
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
