from .common_types import *
import json
import requests
import retry
from ._timeout import timeout
from logzero import logger
DEFAULT_TIMEOUT = 15


def pretty_json(dic: dict):
    output = json.dumps(dic, sort_keys=True, indent=4, separators=(',', ':'))
    print(output)
    return output


def set_timeout(time_out: int or float):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = time_out


class CommonClient:
    """
    client for https://github.com/appium/WebDriverAgent
    """

    def __init__(
            self,
            base_url: str = 'http://localhost:8100',
            desired_caps: dict = None):
        self._base_url = base_url
        self._session_id: str = self.session(desired_caps=desired_caps)

    def screenshot(self, file_path: str = None, raw=None) -> None or str:
        """
        Screenshot and save as file
        :param file_path: file name and path
        :param raw: raw image data (base64)
        :return: raw image data or none
        """
        import base64
        value = self.base_request(GET, "/screenshot").get("value")
        imgdata = base64.b64decode(value)
        if raw:
            return value
        else:
            with open(f'{file_path}', 'wb') as f:
                f.write(imgdata)

    def session(self, desired_caps: dict = None) -> str:
        capabilities = {}
        if desired_caps is not None:
            app_bundle_id = desired_caps.get("appBundleId")
            if app_bundle_id and app_bundle_id.strip():
                capabilities['alwaysMatch'] = {"bundleId": app_bundle_id}
        body = {"capabilities": capabilities}
        data = self.client_request(POST, "/session", body)
        self._session_id = data['sessionId']
        return self._session_id

    def _get_session_id(self) -> str:
        if self._session_id != '':
            return self._session_id
        dated_session_id = self.status()["sessionId"]
        if dated_session_id:
            self._session_id = dated_session_id
        else:
            self._session_id = self.session()
        return self._session_id

    def _gen_element_obj_list(
        self,
        element_id_list: list,
        using: str,
        value: str,
    ) -> list:
        ele_obj_list = []
        for i in range(len(element_id_list)):
            ele_obj_list.append(
                Element(
                    self,
                    using=using,
                    value=value,
                    element_id=element_id_list[i],
                    index=i))
        return ele_obj_list

    def client_request(
            self,
            method: CommonRequestTypes,
            wda_url: str,
            body: dict = None):
        full_url = wda_url
        return self.base_request(method, full_url, body)

    @retry.retry(tries=10, delay=.5)
    def session_request(
            self,
            method: CommonRequestTypes,
            wda_url: str,
            body: dict = None) -> dict:
        session_id = self._get_session_id()
        full_url = (f"/session/{session_id}" + wda_url).strip()
        session_response = self.base_request(method, full_url, body)
        if session_response == "invalid session id":
            logger.debug(f"invalid session {self._session_id}")
            self._session_id = ''
            raise
        elif session_response == 'no such element':
            logger.debug(f"no such element")
            raise
        else:
            return session_response

    def base_request(
            self,
            method: CommonRequestTypes,
            wda_url: str,
            body: dict = None):
        final_url = (self._base_url + wda_url).strip()
        response = requests.request(method=method, url=final_url, json=body)
        response_value = response.json()
        if response.status_code == 404:
            err = response_value.get("value").get("error")
            logger.debug(f"error is {err}")
            return err
        return response_value

    def _percent2pos(self, x: float, y: float) -> tuple:
        """
        According percentage switch to position
        :param x: x coordinate
        :param y: y coordinate
        :return: x, y coordinate
        """
        w, h = self.window_size()
        x, y = int(x * w), int(y * h)
        return x, y

    '''
    Client APIs are Below:
    '''

    def status(self) -> dict:
        status_value = self.base_request(GET, '/status')
        return status_value

    def tap(self, x: float, y: float):
        """
        Screen tap coordinate(only support percentage for compatibility)
        :param x: x coordinate
        :param y: y coordinate
        :return:none
        """
        x, y = self._percent2pos(x, y)
        self.session_request(POST, "/wda/tap/0", {
            "x": x,
            "y": y,
        })

    @property
    def orientation(self) -> str:
        return self.session_request(GET, "/orientation").get("value")

    @orientation.setter
    def orientation(self, orientation: CommonOrientationTypes):
        self.session_request(POST, "/orientation", {
            "orientation": orientation
        })

    def swipe(self,
              from_x: float,
              from_y: float,
              to_x: float,
              to_y: float,
              duration: int or float = 0):
        """
        Swipe screen
        :param from_x: x coordinate
        :param from_y: y coordinate
        :param to_x: x coordinate
        :param to_y: y coordinate
        :param duration: before swipe, press (from_x, from_y) for duration time
        :return: none
        """
        x1, y1 = self._percent2pos(from_x, from_y)
        x2, y2 = self._percent2pos(to_x, to_y)
        self.session_request(POST, "/wda/dragfromtoforduration", {
            "fromX": x1,
            "fromY": y1,
            "toX": x2,
            "toY": y2,
            "duration": duration})
        logger.debug(f"swipe screen form ({x1}, {y1}) to ({x2}, {y2})")

    def flick(self,
              from_x: float,
              from_y: float,
              to_x: float,
              to_y: float,
              duration: int = 100):
        """
        Recommend swipe method
        :param from_x: x coordinate
        :param from_y: y coordinate
        :param to_x: x coordinate
        :param to_y: y coordinate
        :param duration: during swipe, swipe duration time(ms)
        :return: none
        """
        x1, y1 = self._percent2pos(from_x, from_y)
        x2, y2 = self._percent2pos(to_x, to_y)
        self.session_request(POST, "/wda/touch/perform", {
            "actions": [
                {"action": "press", "options": {"x": x1, "y": y1}},
                {"action": "wait", "options": {"ms": duration if duration > 17 else 100}},
                {"action": "moveTo", "options": {"x": x2, "y": y2}},
                {"action": "release", "options": {}}
            ]
        })

    def window_size(self) -> tuple:
        window_value = self.session_request(GET, '/window/size')["value"]
        return window_value["width"], window_value["height"]

    def tap_hold(self, x, y, duration):
        """
        Tap screen and press for duration time
        :param x: x coordinate
        :param y: y coordinate
        :param duration: press (x, y) for duration time
        :return: none
        """
        x, y = self._percent2pos(x, y)
        self.session_request(POST, "/wda/touchAndHold", {
            "x": x,
            "y": y,
            'duration': duration
        })

    def home(self):
        """
        Back to home screen
        :return: none
        """
        try:
            self.base_request(POST, "/wda/homescreen")
        except Exception as e:
            if "Timeout waiting until SpringBoard is visible" in str(e):
                raise e

    def lock(self):
        self.base_request(POST, "/wda/lock")

    def unlock(self):
        self.base_request(POST, "/wda/unlock")

    def healthcheck(self):
        """
        Will go back to home screen
        :return: none
        """
        self.base_request(GET, "/wda/healthcheck")

    def get_lock_state(self) -> str:
        state = self.base_request(GET, "/wda/locked").get("value")
        return LockedStateTypes[state]

    def get_page_source(self) -> str:
        """
        :return: the element tree
        """
        source = self.base_request(GET, "/source").get("value")
        return source

    def get_page_accessible_source(self) -> str:
        """
        :return: accessible resource information (identifiable elements information)
        """
        source = self.base_request(GET, "/wda/accessibleSource")
        return pretty_json(source)

    def hide_keyboard(self):
        """
        Click hide keyboard button
        :return: none
        """
        # todo some errors catch
        self.find_element_by_name("Hide keyboard").click()

    def quit(self):
        """
        Delete session id and back to home screen
        :return: none
        """
        # todo some errors catch
        self.session_request(DELETE, '')

    '''
    Device Apps APIs are Below:
    '''

    def close_app(self, bundle_id: str):
        self.session_request(POST, "/wda/apps/terminate", {
            "bundleId": bundle_id
        })

    @timeout(DEFAULT_TIMEOUT,
             error='Fail to launch app, please check app bundle is existed or not and retry')
    def launch_app(self, bundle_id: str):
        """
        If there are not this app the iOS device will be stuck!!!! Make sure the app is existed in device!
        :param bundle_id: app bundle id
        :return: none
        """
        self.session_request(POST, "/wda/apps/launch", {
            "bundleId": bundle_id
        })

    def get_current_app_info(self) -> dict:
        try:
            return self.session_request(GET, "/wda/apps/list").get("value")[0]
        except BaseException:
            raise ValueError("Unable to get current app info")

    def get_app_state(self, bundle_id: str) -> str:
        state = self.session_request(POST, "/wda/apps/state", {
            "bundleId": bundle_id
        }).get("value")
        return AppStateTypes.get(state)

    '''
    Element APIs are Below:
    '''

    @retry.retry(tries=4, delay=.5)
    def find_element_by_name(self, value: str):
        logger.info(f"find by name {value}")
        return Element(self, using='name', value=value)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_id(self, value: str):
        logger.info(f"find by id {value}")
        return Element(self, using='id', value=value)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_accessibility_id(self, value: str):
        logger.info(f"find by accessibility_id {value}")
        return Element(self, using='accessibility id', value=value)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_xpath(self, value: str):
        logger.info(f"find by xpath {value}")
        return Element(self, using='xpath', value=value)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_text(self, value: str):
        logger.info(f"find by text {value}")
        chain = f"**/XCUIElementTypeAny[`name == '{value}'`]"
        return Element(self, using='class chain', value=chain)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_label(self, value: str):
        logger.info(f"find by label {value}")
        chain = f"**/XCUIElementTypeAny[`label == '{value}'`]"
        return Element(self, using='class chain', value=chain)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_value(self, value: str):
        logger.info(f"find by value {value}")
        chain = f"**/XCUIElementTypeAny[`value == '{value}'`]"
        return Element(self, using='class chain', value=chain)

    @retry.retry(tries=4, delay=.5)
    def find_element_by_class_name(self, value: str):
        logger.info(f"find by class name {value}")
        return Element(self, using='class name', value=value)

    '''
    Elements APIs
    '''

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_name(self, value: str) -> list:
        logger.info(f"find by name {value}")
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='name', value=value), using='name', value=value)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_id(self, value: str) -> list:
        logger.info(f"find by id {value}")
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='id', value=value), using='id', value=value)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_accessibility_id(self, value: str) -> list:
        logger.info(f"find by accessibility_id {value}")
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='accessibility id',
                value=value),
            using='accessibility id',
            value=value)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_xpath(self, value: str) -> list:
        logger.info(f"find by xpath {value}")
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='xpath', value=value), using='xpath', value=value)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_text(self, value: str) -> list:
        logger.info(f"find by text {value}")
        chain = f"**/XCUIElementTypeAny[`name == '{value}'`]"
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='class chain', value=chain), using='class chain', value=chain)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_label(self, value: str) -> list:
        logger.info(f"find by label {value}")
        chain = f"**/XCUIElementTypeAny[`label == '{value}'`]"
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='class chain', value=chain), using='class chain', value=chain)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_value(self, value: str) -> list:
        logger.info(f"find by value {value}")
        chain = f"**/XCUIElementTypeAny[`value == '{value}'`]"
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='class chain', value=chain), using='class chain', value=chain)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_elements_by_class_name(self, value: str) -> list:
        logger.info(f"find by class name {value}")
        element_obj_list = self._gen_element_obj_list(
            element_id_list=self.get_element_id_list(
                using='class name', value=value), using='class name', value=value)
        return element_obj_list

    @retry.retry(tries=4, delay=.5)
    def find_element(self, method: By, value: str):
        logger.info(f"find by {method} {value}")
        find_attr = 'find_element_by_' + method
        return self.__getattribute__(find_attr)(value)

    def find_elements(self, method: By, value: str):
        logger.info(f"find by {method} {value}")
        find_attr = 'find_elements_by_' + method
        return self.__getattribute__(find_attr)(value)

    def get_element_id_list(self, using: str, value: str):
        logger.info(f"find ELEMENTS using {using} value {value}")
        while True:
            element_resp = self.session_request(POST, '/elements', {
                'using': using,
                'value': value
            }).get("value")
            elements_id_list = []
            for _ in element_resp:
                elements_id_list.append({'ELEMENT': _.get('ELEMENT')})
            return elements_id_list


class Element(object):
    def __init__(
            self,
            client: CommonClient,
            using: str,
            value: str,
            element_id: str = None,
            index: int = 0):
        self._client = client
        self._using = using
        self._value = value
        self._index = index
        self._element_id = element_id if element_id is not None else self._get_element_id(
            using=using, value=value)

    @timeout(DEFAULT_TIMEOUT, error='Element Not Found')
    def _get_element_id(self, using: str, value: str) -> str or list:
        logger.info(f"find ELEMENT using {using} value {value}")
        while True:
            element_resp = self._client.session_request(POST, '/element', {
                'using': using,
                'value': value
            }).get("value")
            element_id = element_resp.get("ELEMENT")
            if element_id is not None:
                return element_id
            print("no element and try again")

    def element_request(
            self,
            method: CommonRequestTypes,
            element_url: str,
            body: dict = None):
        wda_url = (f'/element/{self._element_id}' + element_url).strip()
        return self._client.session_request(
            method=method, wda_url=wda_url, body=body)

    def element_shot(self, file_path: str, raw=None) -> None or str:
        """
        Save element as image file
        :param file_path: file name and path
        :param raw: raw image data (base64)
        :return: raw image data or none
        """
        import base64
        value = self.element_request(GET, "/screenshot").get("value")
        imgdata = base64.b64decode(value)
        if raw:
            return value
        else:
            with open(f'{file_path}', 'wb') as f:
                f.write(imgdata)

    @retry.retry(tries=5, delay=.5)
    def click(self):
        logger.info("click element")
        click_response = self.element_request(POST, '/click')
        if click_response == 'stale element reference':
            self._element_id = self._get_element_id(
                using=self._using, value=self._value)
            raise ValueError(
                'The Element is not present or it has expired from the internal cache')
        return click_response

    def send_keys(self, value: str):
        logger.info(f"send keys {value}")
        return self.element_request(POST, '/value', {'value': value})

    def clear(self):
        return self.element_request(POST, "/clear")

    @property
    def rect(self) -> dict:
        rect = self.element_request(GET, '/rect').get("value")
        if rect.get("error"):
            raise ValueError(
                "The Element is not present or it has expired from the internal cache")
        return rect

    @property
    def enable(self) -> bool:
        return self.element_request(GET, '/enabled').get("value")


def remote(base_url: str = None, desired_caps: dict = None) -> CommonClient:
    client = CommonClient(base_url=base_url, desired_caps=desired_caps)
    return client
