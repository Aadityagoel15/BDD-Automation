import json
from playwright.sync_api import sync_playwright


class WebDiscoveryAgent:
    """
    Agent: Web Discovery

    ROLE:
    - Perform read-only UI discovery using Playwright
    - Produce a deterministic, structured page model
    - Observe UI structure without making assumptions

    IMPORTANT:
    - This agent does NOT click elements
    - This agent does NOT test behavior
    - This agent does NOT generate XPath or selectors
    """

    # --------------------------------------------------
    def discover(self, url: str, output_file: str = None) -> dict:
        page_model = {
            "url": url,
            "title": "",
            "inputs": [],
            "buttons": [],
            "links": [],
            "texts": []
        }

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle")

            page_model["title"] = page.title()

            # ---------------- INPUTS ----------------
            for el in page.query_selector_all("input"):
                try:
                    if not el.is_visible():
                        continue

                    page_model["inputs"].append({
                        "label": el.get_attribute("aria-label")
                                 or el.get_attribute("name")
                                 or "",
                        "type": el.get_attribute("type") or "text",
                        "attributes": self._get_attributes(el)
                    })
                except Exception:
                    continue

            # ---------------- BUTTONS ----------------
            for el in page.query_selector_all("button"):
                try:
                    if not el.is_visible():
                        continue

                    text = el.inner_text().strip()
                    if not text:
                        continue

                    page_model["buttons"].append({
                        "text": text,
                        "attributes": self._get_attributes(el)
                    })
                except Exception:
                    continue

            # ---------------- LINKS ----------------
            for el in page.query_selector_all("a"):
                try:
                    if not el.is_visible():
                        continue

                    text = el.inner_text().strip()
                    href = el.get_attribute("href")
                    if text and href:
                        page_model["links"].append({
                            "text": text,
                            "href": href,
                            "attributes": self._get_attributes(el)
                        })
                except Exception:
                    continue

            # ---------------- TEXT NODES (HEADINGS) ----------------
            for el in page.query_selector_all("h1, h2, h3"):
                try:
                    if not el.is_visible():
                        continue

                    text = el.inner_text().strip()
                    if text:
                        page_model["texts"].append(text)
                except Exception:
                    continue

            browser.close()

        # -------- DETERMINISTIC SORTING --------
        page_model["inputs"] = sorted(
            page_model["inputs"],
            key=lambda x: (x["label"], x["type"])
        )
        page_model["buttons"] = sorted(
            page_model["buttons"],
            key=lambda x: x["text"]
        )
        page_model["links"] = sorted(
            page_model["links"],
            key=lambda x: (x["text"], x["href"])
        )
        page_model["texts"] = sorted(set(page_model["texts"]))

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(page_model, f, indent=2)

        return page_model

    # --------------------------------------------------
    def _get_attributes(self, el) -> dict:
        """
        Extract all element attributes (read-only).
        """
        return el.evaluate(
            """(e) => {
                const attrs = {};
                for (const attr of e.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }"""
        )
