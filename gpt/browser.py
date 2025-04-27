import subprocess


class Browser_wrapper:
    """Only for OSX.

    ### Args:
        1. window_geometry = (x, y, w, h)"""

    def __init__(self, **options):
        super().__init__()
        browser = options['browser']
        self._options = options
        self._cmd_to_open = """-e 'tell app \"%s\" to open location \"{url}\"'""" % (
            browser)
        self._cmd_to_open_new = """-e 'tell app \"%s\" to make new document with properties {{URL:\"{url}\"}}'""" % (
            browser)
        self._cmd_to_resize = """-e 'tell app \"%s\" to set bounds of window 1 to {{{x},{y},{w},{h}}}'""" % (
            browser)
        self._cmd_to_close = """-e 'tell app \"%s\" to close current tab of front window'""" % (
            browser)
        self._cmd_to_quit = """-e 'tell app \"%s\" to close every tab of front window'""" % (
            browser)
        self._cmd_force_quit = """-e 'tell app \"%s\" to quit'""" % (
            browser)
        self._cmd_get_active_urls = """-e 'tell app \"%s\" to get URL of every tab of every window'""" % (
            browser)
        self._cmd_get_current_url = """-e 'tell app \"%s\" to get URL of tab {t} of window {w}'""" % (
            browser)
        self._cmd_to_activate = """-e 'tell app \"%s\" to activate'""" % (
            browser)
        self._cmd_get_bounds = """-e 'tell app \"%s\" to get bounds of front window'""" % (
            browser)

    def _run_command(self, cmd, shell=True):
        "Internal helper to run osascript commands."
        return subprocess.run(
            cmd,
            text=True,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )

    def _run_command_Popen(self, cmd, args):
        p = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = p.communicate(cmd)
        return out, err, p.returncode

    def get_window_count(self) -> int:
        """
        Returns the current number of open Safari windows.
        """
        applescript = '''
        tell application "Safari"
          set n to count of windows
          return n as text
        end tell
        '''
        # Build the osascript invocation
        cmd = ["osascript"]
        for line in applescript.strip().splitlines():
            cmd += ["-e", line]

        # Run and capture stdout
        proc = self._run_command(cmd, shell=False)
        # Parse and return as integer
        return int(proc.stdout.strip())

    def open(self, url):
        "Opens browser and navigates to URL; returns (stdout, window, tab)."
        cmd = f"osascript {self._cmd_to_open.format(url=url)} {self._cmd_to_activate}"
        result = self._run_command(cmd).stdout
        w, t = self._get_active_tab_window()
        return result.strip(), w, t

    def open_new_window(self, url):
        "Opens a new window and navigates to URL; returns (stdout, window, tab)."
        x, y, w, h = self._options.get('window_geometry', (0, 0, 700, 900))
        resize = self._cmd_to_resize.format(x=x, y=y, w=w + x, h=h + y)
        cmd = f"osascript {self._cmd_to_open_new.format(url=url)} {resize} {self._cmd_to_activate}"
        out = self._run_command(cmd).stdout
        w_idx, t_idx = self._get_active_tab_window()

        w_idx = self.get_window_count()
        print(f"Window count: {w_idx}")
        return out.strip(), w_idx, t_idx

    def get_window_bounds(self):
        "Returns bounds of the current window."
        cmd = f"osascript {self._cmd_get_bounds}"
        return self._run_command(cmd).stdout.strip()

    def get_all_urls(self):
        "Returns list of all active URLs."
        cmd = f"osascript {self._cmd_get_active_urls}"
        out = self._run_command(cmd).stdout.strip()
        return [u.strip() for u in out.split(",")] if out else []

    def get_current_url(self):
        "Returns current active URL."
        cmd = f"osascript {self._cmd_get_current_url.format(w=self.window, t=self.tab)}"
        out = self._run_command(cmd).stdout.strip()
        return out

    def execute_js(self, js_code=None):
        """
        (Re‑purposed to grab the last assistant reply.)
        Executes JS in Safari and returns the last <assistant> message.
        """
        # JS: collect all assistant texts, reverse the array, take the first element
        js = rf"""{js_code}"""
        # escape quotes/newlines for AppleScript
        js_escaped = js.replace('"', '\\"').replace('\n', ' ')
        osa_cmd = [
            "osascript",
            "-e", f'tell application "Safari" to do JavaScript "{js_escaped}" in tab {self.tab} of window {self.window}'
        ]

        proc = self._run_command(osa_cmd, shell=False)
        return proc.stdout.strip()

    def get_source_code(self, window_index=1, tab_index=1):
        """Fetches HTML source of specified tab and window."""
        script = (
            f"tell application \"Safari\" to tell window {window_index} to "
            f"set src to source of tab {tab_index}\nreturn src"
        )
        cmd = f"osascript -e '{script}'"
        return self._run_command(cmd).stdout.strip()

    def _get_active_tab_window(self):
        cmd = [
            "osascript", "-e",
            'tell application "Safari" to return (index of front window as text) & "," & (index of current tab of front window as text)'
        ]
        out = self._run_command(cmd, shell=False).stdout.strip()
        w, t = out.split(",", 1)
        return int(w), int(t)


class Chrome(Browser_wrapper):
    browser = "Google Chrome"

    def __init__(self, **options):
        options['browser'] = self.browser
        super().__init__(**options)
        self._cmd_get_current_url = (
            "-e 'tell application \"Google Chrome\" to get URL of active tab of front window'"
        )
        self._cmd_get_source = """
            tell application "Google Chrome"
                delay 2
                return execute active tab of front window javascript "document.documentElement.outerHTML"
            end tell
        """
        self._cmd_to_close = (
            "-e 'tell app \"Google Chrome\" to close active tab of front window'"
        )


class Safari(Browser_wrapper):
    browser = "Safari"

    def __init__(self, **options):
        options['browser'] = self.browser
        super().__init__(**options)
        # reuse Browser_wrapper's execute_js & get_source_code

    def open(self, url, window=None, tab=None):
        """
        Opens browser and navigates to URL; returns (stdout, window, tab).
        If `window` and `tab` are None, just does `open location "<url>"`
        """
        # base tell‐script
        open_script = f'tell application "{self.browser}" to open location "{url}"'
        # only tack on window/tab if both are specified
        if window is not None and tab is not None:
            open_script += f" in tab {tab} of window {window}"

        # build the osascript invocation
        cmd = [
            "osascript",
            "-e", open_script,
            # re‑use your activate clause
            *self._cmd_to_activate.split(" -e ")[1:]
        ]

        # run it
        result = self._run_command(cmd, False).stdout.strip()
        # fetch the new active window/tab
        w, t = self._get_active_tab_window()
        return result, w, t
