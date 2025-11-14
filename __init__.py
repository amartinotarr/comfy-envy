from .custom_nodes import HexListToRGBTuples, HexToRGB, ColorDescriptor

NODE_CLASS_MAPPINGS = {
    "HexListToRGBTuples": HexListToRGBTuples,
    "HexToRGB": HexToRGB,
    "ColorDescriptor": ColorDescriptor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HexListToRGBTuples": "Hex List to RGB Tuples",
    "HexToRGB": "Hex to RGB",
    "ColorDescriptor": "Color Descriptor",
}