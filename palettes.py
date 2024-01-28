from base64 import b64encode
from dataclasses import dataclass, field
from io import BytesIO
from typing import ClassVar, Literal, Self, TypeAlias, TypeVar

import palettable
from palettable.palette import Palette
from palettable.utils import load_all_palettes as _load_palettes
from palettable.colorbrewer.colorbrewer import _load_maps_by_type


@dataclass
class Palettes:
    min_colors: int
    normal: list[Palette] = field(default_factory=list)
    reversed_: list[Palette] = field(default_factory=list)
    discrete_data: list[str] = field(default_factory=list)
    continuous_data: list[str] = field(default_factory=list)
    step: int = 1

    image_aspect: ClassVar[tuple[int, int]] = (8, 1)
    image_format: ClassVar[str] = "svg"

    @property
    def num_colors(self) -> int:
        return len(self.normal)

    @property
    def max_colors(self) -> int:
        return self.min_colors + (len(self.normal) - 1) * self.step

    def _num_steps(self, num_colors: int) -> int:
        return round((num_colors - self.min_colors) / self.step)

    def clamp(self, num_colors: int) -> int:
        num_colors = max(self.min_colors, min(num_colors, self.max_colors))
        if self.step == 1:
            return num_colors
        return self.min_colors + self._num_steps(num_colors) * self.step

    def _clamp_index(self, num_colors: int) -> int:
        return max(0, min(self._num_steps(num_colors), len(self.normal) - 1))

    def get(
        self, num_colors: int, reversed_: bool = False
    ) -> Palette:
        """
        Get the palette with the given number of colors.

        Parameters
        ----------
        num_colors : int
            The number of colors in the palette.
        reversed_ : bool, default=False
            Whether to get the reversed palette.

        Returns
        -------
        Palette
        """
        index = self._clamp_index(num_colors)
        return (self.reversed_ if reversed_ else self.normal)[index]

    def get_image(
        self, num_colors: int, display_mode: Literal["discrete", "continuous"]
    ) -> str:
        """
        Get the image of the palette with the given number of colors as a base64-encoded string.

        Parameters
        ----------
        num_colors : int
            The number of colors in the palette.
        display_mode : {"discrete", "continuous"}
            The type of image to get.

        Returns
        -------
        str
            The base64-encoded image.
        """
        image_data = self.continuous_data if display_mode == "continuous" else self.discrete_data
        index = self._clamp_index(num_colors)
        try:
            if image_data[index]:
                return image_data[index]
        except IndexError:
            with open("log.txt", "a") as f:
                f.write(f"{self}: {num_colors} -> {index}\n")
            pass

        palette = self.get(num_colors)
        img = BytesIO()
        palette._write_image(img, display_mode, self.image_format, self.image_aspect)
        if self.image_format == "svg":
            data = img.getvalue().decode("utf-8")
            data = data[data.index("<svg"):]
        else:
            data = b64encode(img.getvalue()).decode("ascii")
        image_data[index] = data
        return data

    def clear_image_cache(self) -> None:
        for i in range(len(self.normal)):
            self.continuous_data[i] = ""
            self.discrete_data[i] = ""

    def _append(self, palette: Palette, reversed_: bool) -> None:
        collection = self.reversed_ if reversed_ else self.normal
        self.continuous_data.append("")
        self.discrete_data.append("")
        collection.append(palette)

    @classmethod
    def generate_palettes(cls, data: dict[str, Palette]) -> "StrDict[Self]":
        palettes = StrDict()
        for name, palette in data.items():
            is_reversed = name.endswith("_r")
            if is_reversed:
                name = name[:-2]
            name, num_colors = name.rsplit("_", 1)
            num_colors = int(num_colors)
            collection = palettes.setdefault(name, cls(num_colors))
            collection._append(palette, is_reversed)
            if num_colors - collection.max_colors > 1:
                collection.step = num_colors - collection.min_colors
        return palettes

    def __str__(self) -> str:
        return (
            f"Palettes: (min_count={self.min_colors}, "
            f"max_count={self.max_colors}, step={self.step})"
        )

    def __repr__(self) -> str:
        return str(self)


T = TypeVar("T")
class StrDict(dict[str, T]):
    def __getattr__(self, name: str) -> T | None:
        return self.get(name)

    def first_value(self) -> T:
        return next(iter(self.values()))


VerbosePaletteMap: TypeAlias = dict[str, dict[str, Palette | dict[str, Palette]]]
PaletteMap: TypeAlias = StrDict[StrDict[Palettes | StrDict[Palettes]]]


def load_all_modules() -> VerbosePaletteMap:
    palette_map = {"colorbrewer": {}}
    for type_ in ["diverging", "sequential", "qualitative"]:
        partial_map = _load_maps_by_type(type_)
        palette_map["colorbrewer"][type_] = partial_map

    for submodule in [
        "cmocean.diverging",
        "cmocean.sequential",
        "cartocolors.diverging",
        "cartocolors.qualitative",
        "cartocolors.sequential",
        "lightbartlein.diverging",
        "lightbartlein.sequential",
        "matplotlib",
        "mycarta",
        "scientific.diverging",
        "scientific.sequential"
    ]:
        module = palettable
        container = palette_map
        parts = submodule.split(".")
        for i, part in enumerate(parts, start=1):
            module = getattr(module, part)
            if i != len(parts):
                container = container.setdefault(part, {})

        get_map_function = getattr(module, "get_map")
        names_and_lengths = getattr(module, "_NAMES_AND_LENGTHS")
        partial_map = _load_palettes(names_and_lengths, get_map_function)
        container[part] = partial_map

    for submodule in [
        "cubehelix",
        "wesanderson",
        "tableau"
    ]:
        partial_map = getattr(palettable, submodule)._get_all_maps()
        palette_map[submodule] = partial_map

    return palette_map


def convert_palette_dict(palettes: VerbosePaletteMap) -> PaletteMap:
    result = StrDict()
    for key, value in sorted(palettes.items()):
        sample_value = next(iter(value.values()))
        if isinstance(sample_value, dict):
            result[key] = convert_palette_dict(value)
        else:
            result[key] = Palettes.generate_palettes(value)
    return result


def load_all_palettes() -> PaletteMap:
    """
    Load all palettes from all modules in palettable.

    Returns
    -------
    PaletteMap
        A nested dictionary of module names and palettes.
        Its keys may be accessed as attributes.
    """
    return convert_palette_dict(load_all_modules())
