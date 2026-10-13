"""Simulates two Streamlit re-runs to prove the result survives a language switch.

Run:  python tools/test_persistence.py
"""

import json
import os
import sys
from contextlib import contextmanager

from streamlit.runtime.scriptrunner import ScriptRunContext
from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_ctx
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")

FAKE = {
    "code": 0,
    "msg": "Success",
    "data": {
        "koc_content": (
            "##### 爆款标题备选\n1. Title A\n2. Title B\n3. Title C\n"
            "##### 正文/口播\nBody line one.\nBody line two.\n"
            "##### 互动/置顶评论\nPinned comment here.\n"
            "---IMAGE_PROMPT: something\n"
        ),
        "image_url": "https://example.com/a.png",
        "video_url": "https://example.com/a.mp4",
    },
}


class FakeResponse:
    status_code = 200

    def json(self):
        return FAKE


def main():
    import requests

    requests.post = lambda *a, **k: FakeResponse()  # stub the Coze call

    at = AppTest.from_file(APP, default_timeout=60)
    at.run()

    if at.exception:
        print("FAIL: initial run raised", at.exception)
        return 1

    # --- simulate pressing the generate button -------------------------------
    at.text_input[0].set_value("https://item.taobao.com/item.htm?id=123").run()
    at.button(key="FormSubmitter" if False else None) if False else None
    # find the generate button by label
    gen = [b for b in at.button if "Generate" in b.label or "生成" in b.label]
    if not gen:
        print("FAIL: could not find the generate button")
        return 1
    gen[0].click().run()

    if at.exception:
        print("FAIL: run raised", at.exception)
        return 1

    def docs(at):
        out = []
        for m in at.markdown:
            out.append(getattr(m, "value", "") or "")
        for e in at.error:
            out.append(getattr(e, "value", "") or "")
        return "\n".join(out)

    def has_result(at):
        # the results heading only renders when a stored result exists
        return "KOC-Ready Marketing Content" in docs(at) or "KOC 级营销内容" in docs(at)

    after_run = has_result(at)
    print("result rendered after generate:", after_run)

    # --- now switch language (the exact bug the user hit) -------------------
    zh = [b for b in at.button if b.label.strip() == "中文"]
    if not zh:
        print("FAIL: language button not found")
        return 1
    zh[0].click().run()

    if at.exception:
        print("FAIL: language switch raised", at.exception)
        return 1

    after_switch = has_result(at)
    chinese_ui = "KOC 级营销内容" in docs(at)
    print("result rendered after switching to Chinese:", after_switch)
    print("UI actually switched to Chinese:", chinese_ui)

    # --- and back to English ------------------------------------------------
    en = [b for b in at.button if b.label.strip() == "English"]
    en[0].click().run()
    back_en = has_result(at)
    print("result rendered after switching back to English:", back_en)

    ok = after_run and after_switch and chinese_ui and back_en
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
