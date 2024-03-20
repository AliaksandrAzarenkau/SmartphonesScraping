from selenium import webdriver
from selenium_stealth import stealth

from fake_useragent import UserAgent


def get_web_driver():

    useragent = UserAgent(platforms='pc')
    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    # options.add_argument("--headless")
    options.add_argument('--disable-blink-features=AutomationControlled')
    prefs = {"profile.default_content_setting_values.geolocation": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
          '''
    })

    stealth(driver,
            user_agent=str(useragent),
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
            )

    return driver
