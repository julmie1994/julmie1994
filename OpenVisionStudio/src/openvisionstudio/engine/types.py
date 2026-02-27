from enum import Enum


class DataType(str, Enum):
    IMAGE = "Image"
    MASK = "Mask"
    CONTOURS = "Contours"
    SCALAR = "Scalar"
    TABLE = "Table"
    ANY = "Any"
