import requests
from bs4 import BeautifulSoup
import re
import os
from typing import TypedDict, List


base_url = 'https://oda.com/no'

Product = TypedDict(
    "Product",
    {
        "name": str,
        "description": str,
        "price": str,
        "unit_price": str,
        "related": List["Product"],
    },
)

Category = TypedDict("Category", {"name": str, "url": str, "path": str})

CategorySection = TypedDict("CategorySection", {"name": str, "path": str})

def with_cache(path: str) -> BeautifulSoup:
    """
    A function the wraps the website with a caching mechanism.

    Reading from the cache if considered first
    """
    root = ".cache"
    url = f"{base_url}{path}"
    filepath = f"{root}{path}.html"

    content = None
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with requests.get(url, stream=True) as res:
            res.raise_for_status()
            # small pages: safe to read into memory
            body = res.content  
            with open(filepath, "wb") as f:
                f.write(body)

        content = BeautifulSoup(body, "html.parser")
    else:
        with open(filepath, "rb") as f:
            body = f.read()
        content = BeautifulSoup(body, "html.parser")

    return content


def read_products(parent_node: BeautifulSoup) -> list[Product]:
    """
    Reads all the products nested within a given parent_node.
    """
    products: list[Product] = []
    children = parent_node.find_all("article", attrs={"data-testid": "product-tile"})
    for child in children:
        entry: Product = {}
        a = child.find(
            "a",
        )
        p = child.find_all("p")
        name = p[0].text
        description = p[1].text
        unit_price = p[2].text

        span = child.find("span")
        entry["name"] = name
        entry["description"] = description
        entry["price"] = span.text
        entry["unit_price"] = unit_price
        if a is not None:
            path: str = a.get("href")
            entry["path"] = path

        products.append(entry)

    return products


def get_category_products(path: str, section: str | None = None) -> list[Product]:
    """
    Reads all products from a given catigory path.

    Tries to read sub sections
    """
    if path is None:
        return "no path"

    full_path = f"/categories/{path}"

    # Some categories hame multiple sections, AKA sub-categories
    if section is not None:
        full_path = f"{full_path}/{section}"

    parsed_content = with_cache(full_path)
    return read_products(parsed_content)


def get_categories() -> list[Category]:
    """
    Retrieves all available categories.
    """
    parsed_content = with_cache("/products")

    categories = parsed_content.find_all(
        "div", class_="k-flex k-align-items-center k-flex--gap-3"
    )
    entries: list[Category] = []
    for category in categories:
        span = category.find("span")
        url = category.find_parent().get("href")
        path = url.split("/")[5]
        entries.append({"name": span.text, "url": url, "path": path})

    return entries


def find_sections(parent_node: BeautifulSoup) -> list[CategorySection]:
    sections: list[CategorySection] = []
    product_sections = parent_node.find_all(
        "h2", id=re.compile("product-category-section")
    )
    for section in product_sections:
        entry: CategorySection = {"name": section.text}
        parent = section.find_parent("a")

        if parent is not None and parent.get("href") is not None:
            path = parent.get("href")
            entry["path"] = path
        sections.append(entry)
    return sections


def get_category_sections(path: str) -> list[CategorySection]:
    """
    Retrieves category sections for a given category path.
    """
    content = with_cache(f"/categories/{path}")

    return find_sections(content)


def read_a_product(path: str) -> Product:
    """
    Reads a single product based on path
    """
    parsed_content = with_cache(f"/products/{path}")

    parent = parsed_content.find("div", attrs={"data-testid": "product-info-section"})
    name = parent.find("h1", attrs={"itemprop": "name"})
    description = parent.find("p")
    price = parent.find("div", re.compile("__productPrice"))
    spans = price.find_all("span", attrs={"aria-hidden": "true"})
    prices = list(map(lambda x: x.text, spans))

    price: str = prices[0]
    unit_price: str = prices[1]

    related: list[Product] = read_products(parsed_content)
    product: Product = {
        "name": name.text,
        "price": price,
        "unit_price": unit_price,
        "description": description.text,
        "related": related,
    }

    return product
