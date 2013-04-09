import base64
import httplib
import logging
import os
import socket

import pyvirtualdisplay
import selenium.common
import selenium.common.exceptions
import selenium.webdriver.chrome.service as chrome_service

from selenium import webdriver

from eagleeye import RedisWorker


logger = logging.getLogger(__name__)

SOCKET_TIMEOUT = 30

class SeleniumWorker(RedisWorker):
    qinput = 'image:http'
    qoutput = 'result:save_image'

    _driver = None
    _service = None

    def __init__(self, *args, **kwargs):
        super(SeleniumWorker, self).__init__(*args, **kwargs)
        # set up the xvfb display
        self.display = pyvirtualdisplay.Display(visible=0, size=(800, 800))
        self.display.start()

        # set socket timeout to kill hung chromedriver connections
        self.original_socket_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(SOCKET_TIMEOUT)

        # Set up the webdriver options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-java')
        self.options.add_argument('--incognito')
        self.options.add_argument('--use-mock-keychain')
        #options.add_argument('--kiosk')
        # http://peter.sh/experiments/chromium-command-line-switches/

    @property
    def service(self):
        if self._service is None:
            self._service = chrome_service.Service('chromedriver')
            self._service.start()
        return self._service

    @property
    def driver(self):
        if self._driver is None:
            self._driver = webdriver.Remote(
                self.service.service_url,
                desired_capabilities=self.options.to_capabilities())
            # These timeout commands don't presently work with
            # chromedriver. Leaving them in in case the chromedriver
            # people suddenly fix this issue:
            # https://code.google.com/p/chromedriver/issues/detail?id=9
            self._driver.set_script_timeout(30)
            self._driver.implicitly_wait(30)
            self._driver.set_page_load_timeout(30)
        return self._driver

    def terminate_driver(self):
        """ Things go wrong with the webdriver; we want to recover robustly """
        logger.info('Terminating webdriver.')
        # Don't quit the driver here because it often hangs
        self._driver = None
        if self._service is not None:
            proc = self._service.process
            try:
                self._service.stop()
                proc.kill()
                # pgroup = os.getpgid(self._service.process.pid)
                # os.killpg(pgroup, ) # XXX
            except Exception:
                # This is really bad...
                pass
        # throw away the old one no matter what
        self._service = None

    def run(self, job):
        target_url = job
        logger.info('Loading %s', target_url)
        screenshot = None
        driver = self.driver
        try:
            driver.get(target_url)
            self.dismiss_alerts()
            logger.info('Loaded %s' % target_url)

            screenshot = driver.get_screenshot_as_base64()

            # try going to a blank page so we get an error now if we can't
            driver.get('about:blank')
        # No timelimiting currently :(
        except socket.timeout:
             logger.info('Terminating overtime connection: %s', target_url)
             self.terminate_driver()
        except (selenium.common.exceptions.WebDriverException,
                httplib.BadStatusLine):
            # just kill it, alright?
            self.terminate_driver()
        except Exception as e:
            print repr(e)
            print 'MAJOR PROBLEM: ', target_url
            self.terminate_driver()
        if screenshot:
            return [screenshot, target_url]

    def dismiss_alerts(self):
        # handle any possible blocking alerts because selenium is stupid
        alert = self.driver.switch_to_alert()
        try:
            alert.dismiss()
            logger.info(
                'Closed alert for %s: %s', self.driver.current_url, alert.text)
        except selenium.common.exceptions.NoAlertPresentException:
            pass

    def __del__(self):
        socket.setdefaulttimeout(self.original_socket_timeout)
        self.terminate_driver()
        self.display.stop()



class WriteScreenshot(RedisWorker):
    qinput = 'result:save_image'

    def run(self, job):
        """ Separate task (and queue: write_screenshot) for writing the
        screenshots to disk, so it can be run wherever the results are
        desired.
        """
        screenshot, url = job
        binary_screenshot = base64.b64decode(screenshot)
        file_name = url.replace('://', '_').replace(':', '_')
        f = open(os.path.join(os.getcwd(), 'out/%s.png' % file_name), 'w')
        f.write(binary_screenshot)
        f.close()
        return url
