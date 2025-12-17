from enum import Enum

class ImageEntityType(str, Enum):
    user = "user"
    team = "team"
    league = "league"

class ImagePurpose(str, Enum):
    profile = "profile"
    logo = "logo"
    cover = "cover"
