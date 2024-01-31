from typing import Literal

import matplotlib
from flask import abort, Flask, render_template, request

matplotlib.use("Agg")

from palettes import load_all_palettes, Palettes

app = Flask(__name__)
data = load_all_palettes()
aspect = Palettes.image_aspect

parameters = {
    "data": data,
    "num_colors": 20,
    "normal": "checked",
    "reversed_": "",
    "discrete": "checked",
    "continuous": "",
    "image_aspect": Palettes.image_aspect,
    "image_format": Palettes.image_format
}

errors = {
    404: (
        "Page not found.",
        "The page you are looking for does not exist."
    ),
    500: (
        "Internal server error.",
        "The server encountered an internal error and was unable to complete your request."
    )
}


# Used for debug
def log(*args) -> None:
    with open("log.txt", "a") as f:
        f.write(" ".join((str(arg) for arg in args)))
        f.write("\n")


@app.route("/")
def index() -> str | None:
    return render_template("index.html", **parameters)


@app.route("/<category>", methods=["GET", "POST"])
def show_category(category: str) -> str:
    try:
        return render_template(
            "palette.html", **parameters, palettes=data[category]
        )
    except KeyError:
        pass
    abort(404)


@app.route("/<category>/<subcategory>", methods=["GET", "POST"])
def show_subcategory(category: str, subcategory: str) -> str:
    try:
        return render_template(
            "palette.html", **parameters, palettes=data[category][subcategory]
        )
    except KeyError:
        pass
    abort(404)


@app.route("/get-palette", methods=["POST"])
def get_palette() -> str:
    collection = data
    categories = request.form.get("categories").split(",")
    for category in categories:
        collection = collection[category]
    palette_collection = collection[request.form.get("id")]

    num_colors = request.form.get("num_colors", type=int)
    # Discrete or continuous
    display_mode = request.form.get("display_mode")

    img_data = palette_collection.get_image(num_colors, display_mode)
    if palette_collection.image_format == "svg":
        return img_data
    return f'<img src="data:image/{palette_collection.image_format};base64,{img_data}">'


def set_pair(value: Literal[0, 1], param_names: tuple[str, str]) -> None:
    parameters[param_names[value]] = "checked"
    parameters[param_names[1 - value]] = ""


def clear_recursively(palettes: dict) -> None:
    for item in palettes.values():
        if isinstance(item, dict):
            clear_recursively(item)
        else:
            item.clear_image_cache()


@app.route("/set-default", methods=["POST"])
def set_default() -> str:
    global aspect
    Palettes.image_aspect = (
        request.form.get("x_scale", type=float),
        request.form.get("y_scale", type=float)
    )
    parameters["image_aspect"] = Palettes.image_aspect
    parameters["num_colors"] = request.form.get("num_colors", type=int)
    set_pair(request.form.get("order", type=int), ("normal", "reversed_"))
    set_pair(request.form.get("display_mode", type=int), ("discrete", "continuous"))

    if Palettes.image_aspect != aspect:
        aspect = Palettes.image_aspect
        clear_recursively(data)
    return "Success"


@app.route("/test-500")
def test_500() -> None:
    raise RuntimeError("Oops!")


def error_handler(code: int) -> tuple[str, int]:
    info = errors[code]
    return render_template(
        "error.html", error_code=code, description=info[0], details=info[1]
    ), code


@app.errorhandler(404)
def page_not_found(error: Exception) -> tuple[str, int]:
    return error_handler(404)


@app.errorhandler(500)
def internal_error(error: Exception) -> tuple[str, int]:
    return error_handler(500)


if __name__ == "__main__":
    app.run()
