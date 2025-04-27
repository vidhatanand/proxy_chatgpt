import json
import time
import base64
import re
from gpt.browser import Safari
from gpt.wait import Wait
from bs4 import BeautifulSoup


class ChatGPT(Safari, Wait):
    def __init__(self, window_geometry=(0, 0, 700, 900)):
        # initialize Safari automation and Wait mixin
        Safari.__init__(self, browser="Safari",
                        window_geometry=window_geometry)
        # Wait.__init__(self, browser="Safari", window_index=1)
        self._current_tab = None
        self._url = "https://chatgpt.com"
        self.window, self.tab = None, None
        self._chat_id = None

        if self._current_tab is None:
            out, w, t = self.open(self._url)
            self.window, self.tab = w, t
            self._current_tab = (out, w, t)

    def login(self, username, password):
        # TODO: navigate to login and fill credentials
        raise NotImplementedError("Login automation not implemented yet.")

    def get_chat_id(self):
        """
        Retrieves the current chat ID by grabbing Safari's current URL
        and parsing out the `/c/<id>` segment.
        """
        url = self.get_current_url()
        match = re.search(r"/c/([^/?]+)", url)
        return match.group(1) if match else ""

    def _fill_prompt(self, prompt: str):
        """
        Injects `prompt` into ChatGPT’s composer and submits it,
        entirely via Safari’s `do JavaScript` (no GUI scripting),
        with a 0.5s delay before clicking Submit.
        """
        b64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")

        js = (
            "(function(){"
            f"const b64 = '{b64}';"
            "const bytes = Uint8Array.from(atob(b64), c=>c.charCodeAt(0));"
            "const str = new TextDecoder('utf-8').decode(bytes);"
            "const el = document.querySelector('#prompt-textarea');"
            "el.focus();"
            "el.innerText = str;"
            "el.dispatchEvent(new Event('input',{bubbles:true}));"
            "setTimeout(function(){"
            "const btn = document.querySelector('button#composer-submit-button');"
            "if(btn) btn.click();"
            "}, 500);"
            "})();"
        )

        return self.execute_js(js)

    def chat(self, prompt, chat_id=None, model_name='gpt-4o', search=False, deep_research=False, wait_for_response_timeout=1200):
        if (self._chat_id is None or (chat_id is not None and chat_id != 'new' and chat_id != self._chat_id)):
            url = self._url if not chat_id or chat_id == 'new' else f"{self._url}/c/{chat_id}"

            if model_name:
                url += f"?model={model_name}"

            out, w, t = self.open(url)

            self.window, self.tab = w, t
            self._current_tab = (out, w, t)

        # print(f"Opened tab: window={self.window}, tab={self.tab}")
        self.wait_for_element('#prompt-textarea')
        time.sleep(1)

        if (search):
            self.wait_for_element(
                'button[data-testid="composer-button-search"]')

            js = r"""
                (() => {
                    const searchBtn = document.querySelector('button[data-testid="composer-button-search"]');
                    if (searchBtn) searchBtn.click();
                })();
            """
            self.execute_js(js)
            time.sleep(0.3)

        if deep_research:
            self.wait_for_element(
                'button[data-testid="composer-button-deep-research"]')
            js = r"""
                (() => {
                    const deepResearch = document.querySelector('button[data-testid="composer-button-deep-research"]');
                    if (deepResearch) deepResearch.click();
                })();
            """
            self.execute_js(js)
            time.sleep(0.3)

        # fill prompt and submit
        self._fill_prompt(prompt)

        # wait for response block, will wait for 1200 seconds by defualt
        self.wait_for_response_to_complete(wait_for_response_timeout)

        self._chat_id = self.get_chat_id()
        return self.get_last_response()

    def get_history(self):
        # If sidebar history isn't visible, open it
        js = r"""
        (() => {
            const el = document.querySelector('#history');
            if (!el) {
                const btn = document.querySelector('button[data-testid="open-sidebar-button"]');
                if (btn) btn.click();
            }
        })();
        """
        self.wait_for_speech_button()
        self.wait_for_element('button[data-testid="open-sidebar-button"]')
        self.execute_js(js)
        # Give the sidebar a moment to render
        # time.sleep(0.5)

        # Fetch the current page HTML
        html = self._get_page_source()
        soup = BeautifulSoup(html, "html.parser")

        # Parse out all chat entries
        history = []
        for a in soup.select("a[data-history-item-link='true']"):
            href = a.get('href', '')
            chat_id = href.rsplit("/", 1)[-1]
            title = a.get_text(strip=True)
            history.append({"id": chat_id, "title": title})
        return history

    def get_last_response(self):
        js = r"""
        (function(){
            const arr = Array.from(
            document.querySelectorAll('[data-message-author-role="assistant"]')
            ).map(el => el.innerText);
            return arr.reverse()[0];
        })()
        """
        return self.execute_js(js)
