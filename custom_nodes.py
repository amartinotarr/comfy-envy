
class HexListToRGBTuples:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hex_list": ("STRING", {"multiline": True, "default": "#FF5733\n#33A1FF\n#808080"}),
                "normalize": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("LIST",)
    RETURN_NAMES = ("rgb_tuples",)
    FUNCTION = "convert_list"
    CATEGORY = "ColorTools"

    def convert_list(self, hex_list, normalize):
        lines = hex_list.strip().splitlines()
        rgb_tuples = []

        for line in lines:
            hex_code = line.strip().lstrip("#")
            if len(hex_code) != 6:
                continue
            try:
                r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                if normalize:
                    rgb_tuples.append((r / 255.0, g / 255.0, b / 255.0))
                else:
                    rgb_tuples.append((r, g, b))
            except ValueError:
                continue

        return (rgb_tuples,)


class HexToRGB:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hex_code": ("STRING", {"default": "#FF5733"}),
                "normalize": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("RGB_TUPLE",)
    RETURN_NAMES = ("rgb",)
    FUNCTION = "convert"
    CATEGORY = "ColorTools"

    def convert(self, hex_code, normalize):
        hex_code = hex_code.lstrip("#")
        if len(hex_code) != 6:
            raise ValueError("Hex code must be 6 characters.")
        r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
        if normalize:
            return ((r / 255.0, g / 255.0, b / 255.0),)
        return ((r, g, b),)


class ColorDescriptor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "rgb": ("RGB_TUPLE",),
                "mode": (["basic", "extended"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("descriptor",)
    FUNCTION = "describe"
    CATEGORY = "ColorTools"

    def describe(self, rgb, mode):
        r, g, b = rgb
        r, g, b = [int(x * 255) if x <= 1 else int(x) for x in (r, g, b)]
        h, s, l = self.rgb_to_hsl(r, g, b)

        base = self.hue_to_color(h)
        if mode == "basic":
            return (base,)
        else:
            qualifier = self.qualify(s, l)
            return (f"{qualifier} {base}",)

    def rgb_to_hsl(self, r, g, b):
        r, g, b = [x / 255.0 for x in (r, g, b)]
        mx, mn = max(r, g, b), min(r, g, b)
        l = (mx + mn) / 2
        d = mx - mn

        if d == 0:
            h = s = 0
        else:
            s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
            if mx == r:
                h = ((g - b) / d + (6 if g < b else 0)) % 6
            elif mx == g:
                h = ((b - r) / d + 2) % 6
            else:
                h = ((r - g) / d + 4) % 6
            h *= 60

        return round(h), round(s * 100), round(l * 100)

    def hue_to_color(self, h):
        if h < 15 or h >= 345:
            return "red"
        elif h < 45:
            return "orange"
        elif h < 75:
            return "yellow"
        elif h < 150:
            return "green"
        elif h < 210:
            return "cyan"
        elif h < 270:
            return "blue"
        elif h < 330:
            return "purple"
        else:
            return "magenta"

    def qualify(self, s, l):
        if s < 20:
            return "neutral"
        elif l < 30:
            return "dark"
        elif l > 80:
            return "light"
        elif s > 70:
            return "vivid"
        elif s < 40:
            return "muted"
        else:
            return "warm" if l > 50 else "cool"
