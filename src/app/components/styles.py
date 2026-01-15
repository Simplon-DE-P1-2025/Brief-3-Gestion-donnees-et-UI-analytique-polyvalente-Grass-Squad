from pathlib import Path


def _load_css_file(filename: str) -> str:
    assets_path = Path(__file__).parent.parent / "assets" / filename
    try:
        return assets_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def get_compact_table_css() -> str:
    css = _load_css_file("compact_table.css")
    return f"<style>\n{css}\n</style>"


def get_separator_html(margin: str = "0.3rem") -> str:
    return f'<hr style="margin: {margin} 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">'


def get_row_separator_html() -> str:
    return '<hr style="margin: 0.1rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.05);">'
