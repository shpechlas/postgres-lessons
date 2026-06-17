from dataclasses import dataclass
from decimal import Decimal

from prompt_toolkit import prompt
from psycopg.rows import class_row
from rich.panel import Panel
from rich.table import Table

from console import console, render_error
from db import get_conn
from validators import ChoiceValidator, NonEmptyValidator, YesNoValidator
from commands import command, CATEGORY_PRODUCT_CATEGORIES


@dataclass
class ProductCategory:
    id: int
    name: str

def _render_product(productCategory: ProductCategory):
    table = Table(show_header=False, box=None, padding=(0, 2))

    table.add_column("Поле", style="bold cyan", width=25)
    table.add_column("Значение", style="white")

    table.add_row("ID", str(productCategory.id))
    table.add_row("Имя категории товара", productCategory.name)

    panel = Panel(
        table,
        expand=False,
        title=f"[bold green]Катешория товара #{productCategory.id}[/bold green]",
        border_style="green",
    )

    console.print(panel)


@command("list product_categories", "список всех категорий товаров", CATEGORY_PRODUCT_CATEGORIES)
def list_products() -> None:
    conn = get_conn()
    table = Table(title="Товары", show_header=True, header_style="bold cyan")

    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("Имя категории товара", style="green", min_width=20)

    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories")
        productCategories: list[ProductCategory] = cur.fetchall()

    for productCategory in productCategories:
        table.add_row(
            str(productCategory.id),
            productCategory.name,
        )
    console.print(table)


@command("show product_category", "информация о категории товара", CATEGORY_PRODUCT_CATEGORIES)
def show_product(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories WHERE id = %s", (_id,))
        productCategorу: ProductCategory | None = cur.fetchone()

    if productCategorу is None:
        render_error(f"Категория товара с ID {_id} не найдена")
        return

    _render_product(productCategorу)


@command("add product_category", "добавить категорию товара (интерактивно)", CATEGORY_PRODUCT_CATEGORIES)
def add_product() -> None:
    conn = get_conn()
    name = prompt("Имя категории товара: ", validator=NonEmptyValidator()).strip()
    conn.execute(
        "INSERT INTO catalog.product_categories (name) VALUES (%s)",
        (name,),
    )
    console.print(f"[green]Категория товара {name} добавлена [/green]")


@command("edit product_category", "редактировать категорию товара", CATEGORY_PRODUCT_CATEGORIES)
def edit_product(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories WHERE id = %s", (_id,))
        productCategorу: ProductCategory | None = cur.fetchone()

    if productCategorу is None:
        render_error(f"Категория товара с ID {_id} не найдена")
        return

    name = prompt("Имя категории товара: ", default=productCategorу.name, validator=NonEmptyValidator()).strip()

    conn.execute(
        """UPDATE catalog.product_categories SET name = %s WHERE id = %s""",
        (name, _id),
    )
    console.print(f"[green]Категория товара {product.sku} ({product.name}) обновлена [/green]")


@command("delete product_category", "удалить категорию товара", CATEGORY_PRODUCT_CATEGORIES)
def delete_product(_id: str) -> None:
    conn = get_conn()
    with conn.cursor(row_factory=class_row(ProductCategory)) as cur:
        cur.execute("SELECT * FROM catalog.product_categories WHERE id = %s", (_id,))
        productCategorу: ProductCategory | None = cur.fetchone()

    if productCategorу is None:
        render_error(f"Категория товара с ID {_id} не найдена")
        return

    _render_product(productCategorу)

    answer = prompt("Вы уверены? (y/n, д/н): ", validator=YesNoValidator())

    if YesNoValidator.is_yes(answer):
        conn.execute("DELETE FROM catalog.product_categories WHERE id = %s", (_id,))
        console.print(f"[green]Категория товара {productCategorу.name} удалена [/green]")


