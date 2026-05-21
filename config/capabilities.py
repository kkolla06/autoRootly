import os
from dotenv import load_dotenv

load_dotenv()

APPIUM_SERVER_URL = "http://127.0.0.1:4723"

CAPS = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:deviceName": os.getenv("DEVICE_NAME"),
    "appium:udid": os.getenv("DEVICE_UDID"),
    "appium:bundleId": os.getenv("APP_BUNDLE_ID"),
    "appium:noReset": True,
    "appium:newCommandTimeout": 120,
    "appium:wdaLaunchTimeout": 120000,
    "appium:wdaConnectionTimeout": 120000,
    "appium:xcodeOrgId": os.getenv("XCODE_ORG_ID", "K2NLUV3HL8"),
    "appium:xcodeSigningId": "Apple Development",
    "appium:updatedWDABundleId": "com.K2NLUV3HL8.WebDriverAgentRunner",
    "appium:allowProvisioningDeviceRegistration": True,
}
