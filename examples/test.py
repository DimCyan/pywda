from pywda import driver

desired_caps = {
    "udid": "",
    "deviceName": "",
    "wdaBundleId": "",
    "appBundleId": ""
}
driver = driver.remote("http://localhost:8100", desired_caps)
