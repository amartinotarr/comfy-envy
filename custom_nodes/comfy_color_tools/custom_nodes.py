
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
        import re
        import json
        
        # Debug: show raw input
        print(f"[comfy_color_tools] Raw input type: {type(hex_list)}, repr: {repr(hex_list[:200]) if len(hex_list) > 200 else repr(hex_list)}")
        
        text = hex_list.strip()
        
        # Handle JSON-serialized input (e.g., from easy showAnything or similar nodes)
        # Input might look like: '[\n]\n    "#c03b88\\n#e06c4d\\n..."'
        # Or a Python list representation: ['#c03b88', '#e06c4d', ...]
        
        # Try to parse as JSON first
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                # It's a JSON array - join elements
                text = '\n'.join(str(item) for item in parsed)
                print(f"[comfy_color_tools] Parsed JSON array with {len(parsed)} elements")
            elif isinstance(parsed, str):
                text = parsed
                print(f"[comfy_color_tools] Parsed JSON string")
        except (json.JSONDecodeError, TypeError):
            pass
        
        # Handle escaped newlines (literal \n in string)
        if '\\n' in text:
            text = text.replace('\\n', '\n')
            print(f"[comfy_color_tools] Unescaped \\n characters")
        
        # Remove JSON artifacts: brackets, quotes
        text = re.sub(r'[\[\]"\']+', '', text)
        
        # Handle multiple separator formats: newlines, commas, semicolons, or spaces
        # First normalize all separators to newlines
        normalized = re.sub(r'[,;\s]+', '\n', text.strip())
        lines = normalized.splitlines()
        rgb_tuples = []

        for line in lines:
            hex_code = line.strip().lstrip("#")
            if not hex_code:
                continue
            if len(hex_code) != 6:
                print(f"[comfy_color_tools] Warning: Skipping invalid hex code '{line.strip()}' (length {len(hex_code)}, expected 6)")
                continue
            try:
                r, g, b = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                if normalize:
                    rgb_tuples.append((r / 255.0, g / 255.0, b / 255.0))
                else:
                    rgb_tuples.append((r, g, b))
            except ValueError as e:
                print(f"[comfy_color_tools] Warning: Failed to parse hex code '{line.strip()}': {e}")
                continue

        if not rgb_tuples:
            print(f"[comfy_color_tools] Warning: No valid hex codes found in input: '{hex_list[:100]}...'")
        else:
            print(f"[comfy_color_tools] Converted {len(rgb_tuples)} hex codes to RGB tuples")

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
