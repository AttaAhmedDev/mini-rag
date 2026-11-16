from enum import Enum

class VectorDBType(Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
    COSINE = "COSINE"
    EUCLIDEAN = "EUCLIDEAN"
    DOT = "DOT"