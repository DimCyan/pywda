# pywda
[appium/WebDriverAgent](https://github.com/appium/WebDriverAgent) Client Library written in Python

## Installation

1. Install WebDriverAgent for iOS devices
   
2. Start WebDriverAgent(the following two methods are recommended)
   
   - Use [Tidevice](https://github.com/alibaba/tidevice) to start WDA without xcodebuild in Windows / MacOS / Linux
   
   - Start with Xcode in MacOS

## Capabilities

### Create client
```py
from pywda import driver

desired_caps = {
    "udid": "",
    "deviceName": "",
    "wdaBundleId": "",
    "appBundleId": ""
}
# desired_caps and agent url are not necessary
driver = driver.remote("http://localhost:8100", desired_caps)

# also create client in default port 8100
driver = driver.remote()
```

### Client Operations
```py
# show status
print(driver.status())

# get session id
print(driver.session())

# save screenshot as png
driver.screenshot("test.png")
# get screenshot base64 data
print(driver.screenshot(raw))

# do healthcheck
driver.healthcheck()

# back to home page
driver.home()

# lock / unlock device operations
driver.lock()
driver.unlock()
print(driver.get_lock_state())

# device orientation operations
print(driver.orientation)
driver.orientation = "PORTRAIT"

# tap device screen(only support percentage for compatibility)
driver.tap(x=0.5, y=0.5)
driver.tap_hold(x=0.5, y=0.5, duration=2)

# swipe device screen(only support percentage for compatibility)
driver.swipe(x=0.5, y=0.5)
# recommend swipe method(duration in ms)
driver.flick(x=0.5, y=0.5, duration=1000)

# get window size
print(driver.window_size())

# get page elements tree(xml or json format)
print(driver.get_page_source())
print(driver.get_page_accessible_source())

# hide keyboard
driver.hide_keyboard()

# app operations
driver.close_app()
driver.launch_app()
print(driver.get_current_app_info())
print(driver.get_app_state())

# close client
driver.quit()
```

### Get element or elements
```python
driver.find_element_by_name()
driver.find_element_by_id()
driver.find_element_by_accessibility_id()
driver.find_element_by_xpath()
driver.find_element_by_text()
driver.find_element_by_label()
driver.find_element_by_value()
driver.find_element_by_class_name()

driver.find_elements_by_name()
driver.find_elements_by_id()
driver.find_elements_by_accessibility_id()
driver.find_elements_by_xpath()
driver.find_elements_by_text()
driver.find_elements_by_label()
driver.find_elements_by_value()
driver.find_elements_by_class_name()

# Also can import By to use
from pywda.driver import By

driver.find_element(By.NAME, 'Test')
driver.find_elements(By.NAME, 'Test')
```

### Element operations
```python
driver.find_elements_by_name('Test').click()
driver.find_elements_by_name('Test').send_keys('sometext')
rect = driver.find_elements_by_name('Test').rect
enable = driver.find_elements_by_name('Test').enable
```
---
## TODO

1. To develop more apis

2. To support alert operations

3. To support Tidevice starting

---
## Thanks
[openatx/facebook-wda](https://github.com/openatx/facebook-wda): Facebook WebDriverAgent Python Client Library (not official)

[openatx/wdapy](https://github.com/openatx/wdapy): Another WebDriverAgent python Client
