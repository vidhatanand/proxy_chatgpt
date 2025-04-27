import time
from bs4 import BeautifulSoup


class Wait:
    def _get_page_source(self):
        osa = (
            f"osascript -e 'tell application \"{self.browser}\" to "
            f"do JavaScript \"document.documentElement.outerHTML\" in tab {self.tab} of window {self.window}'"
        )
        proc = self._run_command(osa)
        return proc.stdout.strip()

    def wait_for_element(self, selector, timeout=15):
        """
        Waits until a CSS selector matches an element in the page HTML.
        selector: any valid CSS selector, e.g. "#prompt-textarea" or "div.my-class"
        """
        start = time.time()
        # print(f"🔍 Waiting for element: {selector}")

        time.sleep(0.1)
        while time.time() - start < timeout:
            html = self._get_page_source()
            soup = BeautifulSoup(html, "html.parser")
            if soup.select_one(selector):
                # print("✅ Element found.", selector)

                time.sleep(0.3) # wait for the element to be fully rendered
                return True
            time.sleep(0.5)

        raise TimeoutError(
            f"❌ Element {selector} not found within {timeout} seconds.")

    def wait_for_speech_button(self, timeout=15):
        """
        Waits until the voice-mode (speech) button appears and is enabled.
        Differentiates by data-testid attribute:
          • Speech button: data-testid="composer-speech-button"
          • Stop button:   data-testid="stop-button"
        """
        start = time.time()
        # print("🔍 Waiting for speech button to enable...")

        while time.time() - start < timeout:
            html = self._get_page_source()
            soup = BeautifulSoup(html, "html.parser")
            # locate speech button by its unique data-testid
            speech_btn = soup.find(
                'button', attrs={'data-testid': 'composer-speech-button'}
            )

            if speech_btn:
                # print("✅ Speech button found and enabled.")
                return True
            time.sleep(0.5)

        raise TimeoutError(
            "❌ Composer-speech-button did not become enabled within timeout"
        )

    def wait_for_stop_button(self, timeout=15):
        """
        Waits until the streaming-stop button appears (state toggles to data-testid="stop-button").
        """
        start = time.time()
        # print("🔍 Waiting for stop button to appear...")

        while time.time() - start < timeout:
            html = self._get_page_source()
            soup = BeautifulSoup(html, "html.parser")
            stop_btn = soup.find(
                'button', attrs={'data-testid': 'stop-button'}
            )
            if stop_btn:
                # print("✅ Stop-button found.")
                return True
            time.sleep(0.5)

        raise TimeoutError(
            "❌ Stop-button did not appear within timeout"
        )

    def wait_for_response_to_complete(self, timeout=60):
        """
        Waits until the response block is fully rendered.
        This is indicated by the absence of a stop button.
        """
        start = time.time()
        # print("🔍 Waiting for response to complete...")

        while time.time() - start < timeout:
            html = self._get_page_source()
            soup = BeautifulSoup(html, "html.parser")
            speech_btn = soup.find(
                'button', attrs={'data-testid': 'composer-speech-button'}
            )

            stop_btn = soup.find(
                'button', attrs={'data-testid': 'stop-button'}
            )
            if not stop_btn and speech_btn:
                time.sleep(0.5)
                # print("✅ Response completed.")
                return True
            time.sleep(0.5)

        raise TimeoutError(
            "❌ Response did not complete within timeout"
        )
