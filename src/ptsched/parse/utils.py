import importlib.resources


def get_grammar():
    return importlib.resources.read_text(
        "ptsched", "data", "ptsched.lark", encoding="utf-8"
    )
