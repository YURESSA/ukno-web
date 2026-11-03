"""Refresh/check the source-derived appendix of backend/docs/api-errors.md."""
import argparse
import ast
from http import HTTPStatus
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCUMENT = ROOT / "backend/docs/api-errors.md"
START = "<!-- BEGIN GENERATED ERROR CATALOG -->"
END = "<!-- END GENERATED ERROR CATALOG -->"


def message_text(node, constants):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Attribute):
        return constants.get(ast.unparse(node))
    if isinstance(node, ast.JoinedStr):
        return "".join(part.value if isinstance(part, ast.Constant) else "{" + ast.unparse(part.value) + "}"
                       for part in node.values)
    return None


def status_code(node):
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "HTTPStatus":
        return HTTPStatus[node.attr].value
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    return None


def read_constants(root):
    tree = ast.parse((root / "backend/core/messages.py").read_text(encoding="utf-8"))
    constants = {}
    for cls in tree.body:
        if isinstance(cls, ast.ClassDef):
            for item in cls.body:
                if isinstance(item, ast.Assign) and isinstance(item.value, ast.Constant):
                    for target in item.targets:
                        constants[f"{cls.name}.{target.id}"] = item.value.value
    return constants


class ErrorVisitor(ast.NodeVisitor):
    def __init__(self, constants):
        self.constants = constants
        self.function = ""
        self.conditions = []
        self.rows = set()

    def add(self, status, message):
        if message:
            condition = self.conditions[-1] if self.conditions else "Ветка возврата ошибки"
            self.rows.add((self.function, str(status), message, condition))

    def visit_FunctionDef(self, node):
        previous = self.function
        self.function = node.name
        self.generic_visit(node)
        self.function = previous

    def visit_If(self, node):
        condition = ast.unparse(node.test)
        self.conditions.append("Если " + condition)
        for statement in node.body:
            self.visit(statement)
        self.conditions[-1] = "Иначе для " + condition
        for statement in node.orelse:
            self.visit(statement)
        self.conditions.pop()

    def visit_ExceptHandler(self, node):
        self.conditions.append("Перехвачено " + (ast.unparse(node.type) if node.type else "исключение"))
        self.generic_visit(node)
        self.conditions.pop()

    def visit_Raise(self, node):
        if isinstance(node.exc, ast.Call) and node.exc.args:
            kind = ast.unparse(node.exc.func)
            if kind in {"ValidationError", "NotFoundError", "ValueError"}:
                status = {"ValidationError": "400*", "NotFoundError": "404*", "ValueError": "исключение"}[kind]
                self.add(status, message_text(node.exc.args[0], self.constants))

    def visit_Return(self, node):
        self.generic_visit(node)
        if not isinstance(node.value, ast.Tuple):
            return
        values = node.value.elts
        status = status_code(values[-1])
        if status is not None and status < 400:
            return
        if status is not None:
            for payload in values[:-1]:
                if isinstance(payload, ast.Dict):
                    for key, message in zip(payload.keys, payload.values):
                        if isinstance(key, ast.Constant) and key.value == "message":
                            self.add(status, message_text(message, self.constants))
                else:
                    self.add(status, message_text(payload, self.constants))
        # Helpers return text to the HTTP handler rather than an HTTP response.
        elif isinstance(values[0], ast.Constant) and (values[0].value is None or values[0].value is False):
            for value in values[1:]:
                self.add("вызывающий код", message_text(value, self.constants))

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == "role_required" and len(node.args) >= 2:
                self.add(403, message_text(node.args[1], self.constants))
            if node.func.id == "get_model_by_name" and len(node.args) >= 4:
                self.add("исключение", message_text(node.args[-1], self.constants))
        self.generic_visit(node)


def cell(text):
    return "`" + text.replace("|", "\\|").replace("\n", "\\n").replace("`", "&#96;") + "`"


def render_catalog(root=ROOT):
    constants = read_constants(root)
    lines = [START, "", "## Каталог сообщений из исходников", "",
             "Раздел обновляется автоматически; вручную редактируются таблицы маршрутов выше.", "",
             "Статусы без звёздочки взяты из явных возвратов. `400*` и `404*` — стандартный статус",
             "типизированного исключения, который вызывающий обработчик может переопределить.",
             "`исключение` и `вызывающий код` требуют сверки с таблицами маршрутов выше.",
             "В частности, загрузка фото культурного пространства возвращает 404, а обработчик фото",
             "новостей преобразует исключение сохранения в 500. Условия в последней колонке —",
             "фрагменты Python из исходного кода, а не отдельные проверки всех входных данных.", ""]
    for path in sorted((root / "backend").rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        if "/scripts/" in relative:
            continue
        visitor = ErrorVisitor(constants)
        visitor.visit(ast.parse(path.read_text(encoding="utf-8")))
        if not visitor.rows:
            continue
        link = "../" + path.relative_to(root / "backend").as_posix()
        lines.extend([f"### [{relative}]({link})", "",
                      "| Функция | HTTP / источник статуса | Точный текст / шаблон | Условие в коде |",
                      "|---|---|---|---|"])
        for function, status, message, condition in sorted(visitor.rows):
            lines.append("| " + " | ".join(cell(value) for value in (function, status, message, condition)) + " |")
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def updated_document(text):
    before, separator, rest = text.partition(START)
    if not separator:
        raise ValueError("Generated catalog start marker is missing")
    _, separator, after = rest.partition(END)
    if not separator:
        raise ValueError("Generated catalog end marker is missing")
    return before + render_catalog() + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the generated catalog is stale")
    args = parser.parse_args()
    original = DOCUMENT.read_text(encoding="utf-8")
    updated = updated_document(original)
    if args.check:
        if original != updated:
            print("Error catalog is stale. Run: python backend/core/scripts/generate_error_docs.py")
            return 1
        print("Error catalog is up to date.")
    else:
        DOCUMENT.write_text(updated, encoding="utf-8", newline="\n")
        print("Updated backend/docs/api-errors.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
