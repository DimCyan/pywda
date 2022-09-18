import enum


AppStateTypes = {
    1: "App exists but does not survive or App does not exist",
    2: "App exists but is in the background",
    4: "App exists and is in the foreground"}

LockedStateTypes = {
    True: "Device is locked",
    False: "Device is unlocked"}


class CommonOrientationTypes(str, enum.Enum):
    LANDSCAPE = "LANDSCAPE"
    PORTRAIT = "PORTRAIT"
    UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT = "UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT"
    UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN = "UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN"


LANDSCAPE = CommonOrientationTypes.LANDSCAPE
PORTRAIT = CommonOrientationTypes.PORTRAIT
UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT = CommonOrientationTypes.UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT
UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN = CommonOrientationTypes.UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN


class CommonRequestTypes(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


GET = CommonRequestTypes.GET
POST = CommonRequestTypes.POST
DELETE = CommonRequestTypes.DELETE


class By(str, enum.Enum):
    XPATH = "xpath"
    ID = "id"
    NAME = "name"
    VALUE = "value"
    TEXT = "text"


XPATH = By.XPATH
ID = By.ID
NAME = By.NAME
VALUE = By.VALUE
TEXT = By.TEXT
