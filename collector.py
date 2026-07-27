# # # # # version 2.0 try:- WORKING -
# # # # from playwright.sync_api import sync_playwright
# # # # import pandas as pd
# # # # import time

# # # # from config import *


# # # # class LinkedInCollector:

# # # #     def __init__(self):
# # # #         self.jobs = []
# # # #         self.play = sync_playwright().start()
# # # #         self.browser = self.play.chromium.launch(headless=False)
# # # #         self.page = self.browser.new_page()

# # # #     def login(self):
# # # #         self.page.goto("https://www.linkedin.com/login")
# # # #         print("=" * 60)
# # # #         print("Login manually.")
# # # #         print("Complete MFA if needed.")
# # # #         print("Then press ENTER.")
# # # #         print("=" * 60)
# # # #         input()

# # # #     def safe_text(self, locator, default=""):
# # # #         """Return inner_text() or a default if the locator times out / has no match."""
# # # #         try:
# # # #             if locator.count() == 0:
# # # #                 return default
# # # #             return locator.first.inner_text(timeout=5000).strip()
# # # #         except Exception:
# # # #             return default

# # # #     def collect_jobs(self):

# # # #         for keyword in SEARCH_TERMS:

# # # #             print(f"\nSearching {keyword}")

# # # #             url = (
# # # #                 "https://www.linkedin.com/jobs/search/"
# # # #                 f"?keywords={keyword.replace(' ', '%20')}"
# # # #             )

# # # #             self.page.goto(url)
# # # #             time.sleep(5)

# # # #             for page_number in range(PAGES_TO_SCAN):

# # # #                 print(f"Page {page_number + 1}")

# # # #                 self.page.mouse.wheel(0, 100000)
# # # #                 time.sleep(2)

# # # #                 cards = self.page.locator(".job-card-container").all()

# # # #                 print(f"Found {len(cards)} cards")

# # # #                 if not cards:
# # # #                     print("No job cards found on this page — selector may be stale.")

# # # #                 for i, card in enumerate(cards):

# # # #                     try:
# # # #                         # Scroll the card into view before clicking — LinkedIn
# # # #                         # sometimes ignores clicks on elements outside the viewport.
# # # #                         card.scroll_into_view_if_needed(timeout=5000)

# # # #                         title = self.safe_text(card.locator("strong"))

# # # #                         # Fallback selectors — LinkedIn renames these classes often,
# # # #                         # so try a couple of variants instead of hard-failing.
# # # #                         company = self.safe_text(
# # # #                             card.locator(
# # # #                                 ".artdeco-entity-lockup__subtitle, "
# # # #                                 ".job-card-container__primary-description, "
# # # #                                 ".job-card-container__company-name"
# # # #                             )
# # # #                         )

# # # #                         location = self.safe_text(
# # # #                             card.locator(
# # # #                                 ".job-card-container__metadata-item, "
# # # #                                 ".artdeco-entity-lockup__caption, "
# # # #                                 "ul.job-card-container__metadata-wrapper li"
# # # #                             )
# # # #                         )

# # # #                         href = None
# # # #                         link_locator = card.locator("a").first
# # # #                         if link_locator.count():
# # # #                             href = link_locator.get_attribute("href", timeout=5000)

# # # #                         # Click to load the description pane on the right.
# # # #                         card.click(timeout=5000)
# # # #                         time.sleep(2)

# # # #                         description = self.safe_text(
# # # #                             self.page.locator(
# # # #                                 '[data-sdui-component="com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"], '
# # # #                                 ".jobs-description__content, "
# # # #                                 ".jobs-box__html-content"
# # # #                             )
# # # #                         )

# # # #                         if description:
# # # #                             print("=" * 80)
# # # #                             print(description[:500])
# # # #                             print("=" * 80)

# # # #                         self.jobs.append({
# # # #                             "Title": title,
# # # #                             "Company": company,
# # # #                             "Location": location,
# # # #                             "Description": description,
# # # #                             "URL": href,
# # # #                             "Keyword": keyword,
# # # #                         })

# # # #                         print(f"  [{i+1}/{len(cards)}] {title or '(no title)'} @ {company or '(no company)'}")

# # # #                     except Exception as e:
# # # #                         print(f"Error on card {i+1}: {e}")
# # # #                         # Still record whatever we managed to grab, so a bad
# # # #                         # card doesn't silently drop the whole row.
# # # #                         continue

# # # #                 next_button = self.page.locator("button[aria-label='View next page']")

# # # #                 if next_button.count():
# # # #                     try:
# # # #                         next_button.click(timeout=5000)
# # # #                         time.sleep(4)
# # # #                     except Exception as e:
# # # #                         print(f"Couldn't click next page: {e}")
# # # #                         break
# # # #                 else:
# # # #                     break

# # # #     def save(self):
# # # #         df = pd.DataFrame(self.jobs)

# # # #         if df.empty:
# # # #             print("No jobs collected — nothing to save.")
# # # #             self.browser.close()
# # # #             self.play.stop()
# # # #             return

# # # #         df.drop_duplicates(subset=["URL"], inplace=True)
# # # #         df.to_csv(OUTPUT_CSV, index=False)

# # # #         print()
# # # #         print("=" * 60)
# # # #         print(f"Saved {len(df)} jobs.")
# # # #         print("=" * 60)

# # # #         self.browser.close()
# # # #         self.play.stop()

# # # # VERSION 3 IMPROVING:

# # # import os
# # # from playwright.sync_api import sync_playwright
# # # import pandas as pd
# # # import time

# # # from config import *

# # # AUTH_FILE = "linkedin_auth.json"


# # # class LinkedInCollector:

# # #     def __init__(self):
# # #         self.jobs = []
# # #         self.play = sync_playwright().start()
# # #         self.browser = self.play.chromium.launch(headless=False)

# # #         if os.path.exists(AUTH_FILE):
# # #             # Reuse saved cookies/session — skips the login screen entirely.
# # #             self.context = self.browser.new_context(storage_state=AUTH_FILE)
# # #         else:
# # #             self.context = self.browser.new_context()

# # #         self.page = self.context.new_page()

# # #     def login(self):
# # #         # If we already loaded a saved session, verify it's still valid
# # #         # before asking for a manual login again.
# # #         if os.path.exists(AUTH_FILE):
# # #             self.page.goto("https://www.linkedin.com/feed/")
# # #             time.sleep(3)
# # #             if "linkedin.com/feed" in self.page.url:
# # #                 print("Reusing saved session — skipping login.")
# # #                 return
# # #             else:
# # #                 print("Saved session expired — please log in again.")

# # #         self.page.goto("https://www.linkedin.com/login")
# # #         print("=" * 60)
# # #         print("Login manually.")
# # #         print("Complete MFA if needed.")
# # #         print("Then press ENTER.")
# # #         print("=" * 60)
# # #         input()

# # #         # Persist cookies/local storage so future runs skip this step.
# # #         self.context.storage_state(path=AUTH_FILE)
# # #         print(f"Session saved to {AUTH_FILE}.")

# # #     def safe_text(self, locator, default=""):
# # #         """Return inner_text() or a default if the locator times out / has no match."""
# # #         try:
# # #             if locator.count() == 0:
# # #                 return default
# # #             return locator.first.inner_text(timeout=5000).strip()
# # #         except Exception:
# # #             return default

# # #     def collect_jobs(self):

# # #         for keyword in SEARCH_TERMS:

# # #             print(f"\nSearching {keyword}")

# # #             url = (
# # #                 "https://www.linkedin.com/jobs/search/"
# # #                 f"?keywords={keyword.replace(' ', '%20')}"
# # #             )

# # #             self.page.goto(url)
# # #             time.sleep(5)

# # #             for page_number in range(PAGES_TO_SCAN):

# # #                 print(f"Page {page_number + 1}")

# # #                 self.page.mouse.wheel(0, 100000)
# # #                 time.sleep(2)

# # #                 cards = self.page.locator(".job-card-container").all()

# # #                 print(f"Found {len(cards)} cards")

# # #                 if not cards:
# # #                     print("No job cards found on this page — selector may be stale.")

# # #                 for i, card in enumerate(cards):

# # #                     # Defaults so a partial failure still produces a row
# # #                     # instead of losing the card entirely.
# # #                     title = ""
# # #                     company = ""
# # #                     location = ""
# # #                     href = None
# # #                     description = ""

# # #                     try:
# # #                         # Scroll into view and click FIRST — clicking can
# # #                         # change which card LinkedIn treats as "selected"
# # #                         # and re-render its contents, and some fields
# # #                         # (especially the description pane) aren't populated
# # #                         # until after the click fires.
# # #                         card.scroll_into_view_if_needed(timeout=5000)
# # #                         card.click(timeout=5000)
# # #                         time.sleep(2)

# # #                         title = self.safe_text(card.locator("strong"))

# # #                         # Fallback selectors — LinkedIn renames these classes often,
# # #                         # so try a couple of variants instead of hard-failing.
# # #                         company = self.safe_text(
# # #                             card.locator(
# # #                                 ".artdeco-entity-lockup__subtitle, "
# # #                                 ".job-card-container__primary-description, "
# # #                                 ".job-card-container__company-name"
# # #                             )
# # #                         )

# # #                         location = self.safe_text(
# # #                             card.locator(
# # #                                 ".job-card-container__metadata-item, "
# # #                                 ".artdeco-entity-lockup__caption, "
# # #                                 "ul.job-card-container__metadata-wrapper li"
# # #                             )
# # #                         )

# # #                         link_locator = card.locator("a").first
# # #                         if link_locator.count():
# # #                             raw_href = link_locator.get_attribute("href", timeout=5000)
# # #                             if raw_href and raw_href.startswith("/"):
# # #                                 href = f"https://www.linkedin.com{raw_href}"
# # #                             else:
# # #                                 href = raw_href

# # #                         description = self.safe_text(
# # #                             self.page.locator(
# # #                                 '[data-sdui-component="com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"], '
# # #                                 ".jobs-description__content, "
# # #                                 ".jobs-box__html-content"
# # #                             )
# # #                         )

# # #                         if description:
# # #                             print("=" * 80)
# # #                             print(description[:500])
# # #                             print("=" * 80)

# # #                         print(f"  [{i+1}/{len(cards)}] {title or '(no title)'} @ {company or '(no company)'}")

# # #                     except Exception as e:
# # #                         print(f"Error on card {i+1}: {e}")
# # #                         # Fall through — whatever fields were captured
# # #                         # before the exception are still recorded below.

# # #                     self.jobs.append({
# # #                         "Title": title,
# # #                         "Company": company,
# # #                         "Location": location,
# # #                         "Description": description,
# # #                         "URL": href,
# # #                         "Keyword": keyword,
# # #                     })

# # #                 next_button = self.page.locator("button[aria-label='View next page']")

# # #                 if next_button.count():
# # #                     try:
# # #                         next_button.click(timeout=5000)
# # #                         time.sleep(4)
# # #                     except Exception as e:
# # #                         print(f"Couldn't click next page: {e}")
# # #                         break
# # #                 else:
# # #                     break

# # #     def save(self):
# # #         df = pd.DataFrame(self.jobs)

# # #         if df.empty:
# # #             print("No jobs collected — nothing to save.")
# # #             self.context.close()
# # #             self.browser.close()
# # #             self.play.stop()
# # #             return

# # #         df.drop_duplicates(subset=["URL"], inplace=True)
# # #         df.to_csv(OUTPUT_CSV, index=False)

# # #         print()
# # #         print("=" * 60)
# # #         print(f"Saved {len(df)} jobs.")
# # #         print("=" * 60)

# # #         self.context.close()
# # #         self.browser.close()
# # #         self.play.stop()


# # # version 4.0 : 
# # import os
# # from playwright.sync_api import sync_playwright
# # import pandas as pd
# # import time

# # from config import *

# # AUTH_FILE = "linkedin_auth.json"


# # class LinkedInCollector:

# #     def __init__(self):
# #         self.jobs = []
# #         self.play = sync_playwright().start()
# #         self.browser = self.play.chromium.launch(headless=False)

# #         if os.path.exists(AUTH_FILE):
# #             # Reuse saved cookies/session — skips the login screen entirely.
# #             self.context = self.browser.new_context(storage_state=AUTH_FILE)
# #         else:
# #             self.context = self.browser.new_context()

# #         self.page = self.context.new_page()

# #     def login(self):
# #         # If we already loaded a saved session, verify it's still valid
# #         # before asking for a manual login again.
# #         if os.path.exists(AUTH_FILE):
# #             self.page.goto("https://www.linkedin.com/feed/")
# #             time.sleep(3)
# #             if "linkedin.com/feed" in self.page.url:
# #                 print("Reusing saved session — skipping login.")
# #                 return
# #             else:
# #                 print("Saved session expired — please log in again.")

# #         self.page.goto("https://www.linkedin.com/login")
# #         print("=" * 60)
# #         print("Login manually.")
# #         print("Complete MFA if needed.")
# #         print("Then press ENTER.")
# #         print("=" * 60)
# #         input()

# #         # Persist cookies/local storage so future runs skip this step.
# #         self.context.storage_state(path=AUTH_FILE)
# #         print(f"Session saved to {AUTH_FILE}.")

# #     def safe_text(self, locator, default=""):
# #         """Return inner_text() or a default if the locator times out / has no match."""
# #         try:
# #             if locator.count() == 0:
# #                 return default
# #             return locator.first.inner_text(timeout=5000).strip()
# #         except Exception:
# #             return default

# #     def collect_jobs(self):

# #         for keyword in SEARCH_TERMS:

# #             print(f"\nSearching {keyword}")

# #             url = (
# #                 "https://www.linkedin.com/jobs/search/"
# #                 f"?keywords={keyword.replace(' ', '%20')}"
# #             )

# #             self.page.goto(url)
# #             time.sleep(5)

# #             for page_number in range(PAGES_TO_SCAN):

# #                 print(f"Page {page_number + 1}")

# #                 # LinkedIn lazy-loads job cards as you scroll — jumping straight
# #                 # to the bottom skips the scroll events that trigger loading,
# #                 # so only the first ~7 cards ever render. Scroll in smaller
# #                 # increments with pauses so each batch has time to load.
# #                 previous_count = 0
# #                 stable_rounds = 0

# #                 # The job results list is its own scrollable panel, not the
# #                 # page body — page-level mouse.wheel does nothing once the
# #                 # cursor isn't over that panel. Scroll the container's
# #                 # scrollTop directly via JS instead.
# #                 scroll_container_selector = ".jobs-search-results-list, .scaffold-layout__list-container, .scaffold-layout__list"

# #                 for _ in range(15):
# #                     scrolled = self.page.evaluate(
# #                         """(sel) => {
# #                             const el = document.querySelector(sel);
# #                             if (el) {
# #                                 el.scrollTop += 1200;
# #                                 return true;
# #                             }
# #                             return false;
# #                         }""",
# #                         scroll_container_selector,
# #                     )

# #                     if not scrolled:
# #                         # Fallback: container selector didn't match — try
# #                         # scrolling the last job card into view instead,
# #                         # which forces the same lazy-load behavior.
# #                         cards_now = self.page.locator(".job-card-container").all()
# #                         if cards_now:
# #                             cards_now[-1].scroll_into_view_if_needed(timeout=3000)

# #                     time.sleep(1)

# #                     current_count = self.page.locator(".job-card-container").count()

# #                     if current_count == previous_count:
# #                         stable_rounds += 1
# #                         if stable_rounds >= 3:
# #                             # No new cards after 3 consecutive scrolls — assume
# #                             # we've reached the end of this page's list.
# #                             break
# #                     else:
# #                         stable_rounds = 0

# #                     previous_count = current_count

# #                 print(f"Loaded {previous_count} cards after scrolling.")

# #                 cards = self.page.locator(".job-card-container").all()

# #                 print(f"Found {len(cards)} cards")

# #                 if not cards:
# #                     print("No job cards found on this page — selector may be stale.")

# #                 for i, card in enumerate(cards):

# #                     # Defaults so a partial failure still produces a row
# #                     # instead of losing the card entirely.
# #                     title = ""
# #                     company = ""
# #                     location = ""
# #                     href = None
# #                     description = ""

# #                     try:
# #                         # Scroll into view and click FIRST — clicking can
# #                         # change which card LinkedIn treats as "selected"
# #                         # and re-render its contents, and some fields
# #                         # (especially the description pane) aren't populated
# #                         # until after the click fires.
# #                         card.scroll_into_view_if_needed(timeout=5000)
# #                         card.click(timeout=5000)
# #                         time.sleep(2)

# #                         title = self.safe_text(card.locator("strong"))

# #                         # Fallback selectors — LinkedIn renames these classes often,
# #                         # so try a couple of variants instead of hard-failing.
# #                         company = self.safe_text(
# #                             card.locator(
# #                                 ".artdeco-entity-lockup__subtitle, "
# #                                 ".job-card-container__primary-description, "
# #                                 ".job-card-container__company-name"
# #                             )
# #                         )

# #                         location = self.safe_text(
# #                             card.locator(
# #                                 ".job-card-container__metadata-item, "
# #                                 ".artdeco-entity-lockup__caption, "
# #                                 "ul.job-card-container__metadata-wrapper li"
# #                             )
# #                         )

# #                         link_locator = card.locator("a").first
# #                         if link_locator.count():
# #                             raw_href = link_locator.get_attribute("href", timeout=5000)
# #                             if raw_href and raw_href.startswith("/"):
# #                                 href = f"https://www.linkedin.com{raw_href}"
# #                             else:
# #                                 href = raw_href

# #                         description = self.safe_text(
# #                             self.page.locator(
# #                                 '[data-sdui-component="com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"], '
# #                                 ".jobs-description__content, "
# #                                 ".jobs-box__html-content"
# #                             )
# #                         )

# #                         if description:
# #                             print("=" * 80)
# #                             print(description[:500])
# #                             print("=" * 80)

# #                         print(f"  [{i+1}/{len(cards)}] {title or '(no title)'} @ {company or '(no company)'}")

# #                     except Exception as e:
# #                         print(f"Error on card {i+1}: {e}")
# #                         # Fall through — whatever fields were captured
# #                         # before the exception are still recorded below.

# #                     self.jobs.append({
# #                         "Title": title,
# #                         "Company": company,
# #                         "Location": location,
# #                         "Description": description,
# #                         "URL": href,
# #                         "Keyword": keyword,
# #                     })

# #                 next_button = self.page.locator("button[aria-label='View next page']")

# #                 if next_button.count():
# #                     try:
# #                         next_button.click(timeout=5000)
# #                         time.sleep(4)
# #                     except Exception as e:
# #                         print(f"Couldn't click next page: {e}")
# #                         break
# #                 else:
# #                     break

# #     def save(self):
# #         df = pd.DataFrame(self.jobs)

# #         if df.empty:
# #             print("No jobs collected — nothing to save.")
# #             self.context.close()
# #             self.browser.close()
# #             self.play.stop()
# #             return

# #         df.drop_duplicates(subset=["URL"], inplace=True)
# #         df.to_csv(OUTPUT_CSV, index=False)

# #         print()
# #         print("=" * 60)
# #         print(f"Saved {len(df)} jobs.")
# #         print("=" * 60)

# #         self.context.close()
# #         self.browser.close()
# #         self.play.stop()


# # trying to get past 7 jobs in a page:
# import os
# from playwright.sync_api import sync_playwright
# import pandas as pd
# import time

# from config import *

# AUTH_FILE = "linkedin_auth.json"


# class LinkedInCollector:

#     def __init__(self):
#         self.jobs = []
#         self.play = sync_playwright().start()
#         self.browser = self.play.chromium.launch(headless=False)

#         if os.path.exists(AUTH_FILE):
#             # Reuse saved cookies/session — skips the login screen entirely.
#             self.context = self.browser.new_context(storage_state=AUTH_FILE)
#         else:
#             self.context = self.browser.new_context()

#         self.page = self.context.new_page()

#     def login(self):
#         # If we already loaded a saved session, verify it's still valid
#         # before asking for a manual login again.
#         if os.path.exists(AUTH_FILE):
#             self.page.goto("https://www.linkedin.com/feed/")
#             time.sleep(3)
#             if "linkedin.com/feed" in self.page.url:
#                 print("Reusing saved session — skipping login.")
#                 return
#             else:
#                 print("Saved session expired — please log in again.")

#         self.page.goto("https://www.linkedin.com/login")
#         print("=" * 60)
#         print("Login manually.")
#         print("Complete MFA if needed.")
#         print("Then press ENTER.")
#         print("=" * 60)
#         input()

#         # Persist cookies/local storage so future runs skip this step.
#         self.context.storage_state(path=AUTH_FILE)
#         print(f"Session saved to {AUTH_FILE}.")

#     def safe_text(self, locator, default=""):
#         """Return inner_text() or a default if the locator times out / has no match."""
#         try:
#             if locator.count() == 0:
#                 return default
#             return locator.first.inner_text(timeout=5000).strip()
#         except Exception:
#             return default

#     def collect_jobs(self):

#         for keyword in SEARCH_TERMS:

#             print(f"\nSearching {keyword}")

#             url = (
#                 "https://www.linkedin.com/jobs/search/"
#                 f"?keywords={keyword.replace(' ', '%20')}"
#             )

#             self.page.goto(url)
#             time.sleep(5)

#             for page_number in range(PAGES_TO_SCAN):

#                 print(f"Page {page_number + 1}")

#                 # LinkedIn lazy-loads job cards as you scroll — jumping straight
#                 # to the bottom skips the scroll events that trigger loading,
#                 # so only the first ~7 cards ever render. Scroll in smaller
#                 # increments with pauses so each batch has time to load.
#                 # LinkedIn lazy-loads job cards as you scroll — jumping straight
#                 # to the bottom skips the scroll events that trigger loading,
#                 # so only the first ~7 cards ever render. Rather than finding
#                 # the scroll container ourselves, just repeatedly scroll the
#                 # LAST currently-loaded card into view — Playwright's
#                 # scroll_into_view_if_needed automatically scrolls whatever
#                 # nested scrollable ancestor is needed, no selector required.
#                 previous_count = 0
#                 stable_rounds = 0

#                 for _ in range(20):
#                     cards_now = self.page.locator(".job-card-container").all()

#                     if cards_now:
#                         try:
#                             cards_now[-1].scroll_into_view_if_needed(timeout=3000)
#                         except Exception:
#                             pass

#                     time.sleep(1)

#                     current_count = self.page.locator(".job-card-container").count()

#                     if current_count == previous_count:
#                         stable_rounds += 1
#                         if stable_rounds >= 3:
#                             # No new cards after 3 consecutive scrolls — assume
#                             # we've reached the end of this page's list.
#                             break
#                     else:
#                         stable_rounds = 0

#                     previous_count = current_count

#                 print(f"Loaded {previous_count} cards after scrolling.")

#                 cards = self.page.locator(".job-card-container").all()

#                 print(f"Found {len(cards)} cards")

#                 if not cards:
#                     print("No job cards found on this page — selector may be stale.")

#                 for i, card in enumerate(cards):

#                     # Defaults so a partial failure still produces a row
#                     # instead of losing the card entirely.
#                     title = ""
#                     company = ""
#                     location = ""
#                     href = None
#                     description = ""

#                     try:
#                         # Scroll into view and click FIRST — clicking can
#                         # change which card LinkedIn treats as "selected"
#                         # and re-render its contents, and some fields
#                         # (especially the description pane) aren't populated
#                         # until after the click fires.
#                         card.scroll_into_view_if_needed(timeout=5000)
#                         card.click(timeout=5000)
#                         time.sleep(2)

#                         title = self.safe_text(card.locator("strong"))

#                         # Fallback selectors — LinkedIn renames these classes often,
#                         # so try a couple of variants instead of hard-failing.
#                         company = self.safe_text(
#                             card.locator(
#                                 ".artdeco-entity-lockup__subtitle, "
#                                 ".job-card-container__primary-description, "
#                                 ".job-card-container__company-name"
#                             )
#                         )

#                         location = self.safe_text(
#                             card.locator(
#                                 ".job-card-container__metadata-item, "
#                                 ".artdeco-entity-lockup__caption, "
#                                 "ul.job-card-container__metadata-wrapper li"
#                             )
#                         )

#                         link_locator = card.locator("a").first
#                         if link_locator.count():
#                             raw_href = link_locator.get_attribute("href", timeout=5000)
#                             if raw_href and raw_href.startswith("/"):
#                                 href = f"https://www.linkedin.com{raw_href}"
#                             else:
#                                 href = raw_href

#                         description = self.safe_text(
#                             self.page.locator(
#                                 '[data-sdui-component="com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"], '
#                                 ".jobs-description__content, "
#                                 ".jobs-box__html-content"
#                             )
#                         )

#                         if description:
#                             print("=" * 80)
#                             print(description[:500])
#                             print("=" * 80)

#                         print(f"  [{i+1}/{len(cards)}] {title or '(no title)'} @ {company or '(no company)'}")

#                     except Exception as e:
#                         print(f"Error on card {i+1}: {e}")
#                         # Fall through — whatever fields were captured
#                         # before the exception are still recorded below.

#                     self.jobs.append({
#                         "Title": title,
#                         "Company": company,
#                         "Location": location,
#                         "Description": description,
#                         "URL": href,
#                         "Keyword": keyword,
#                     })

#                 next_button = self.page.locator("button[aria-label='View next page']")

#                 if next_button.count():
#                     try:
#                         next_button.click(timeout=5000)
#                         time.sleep(4)
#                     except Exception as e:
#                         print(f"Couldn't click next page: {e}")
#                         break
#                 else:
#                     break

#     def save(self):
#         df = pd.DataFrame(self.jobs)

#         if df.empty:
#             print("No jobs collected — nothing to save.")
#             self.context.close()
#             self.browser.close()
#             self.play.stop()
#             return

#         df.drop_duplicates(subset=["URL"], inplace=True)
#         df.to_csv(OUTPUT_CSV, index=False)

#         print()
#         print("=" * 60)
#         print(f"Saved {len(df)} jobs.")
#         print("=" * 60)

#         self.context.close()
#         self.browser.close()
#         self.play.stop()








# version: trying for all:
import os
from playwright.sync_api import sync_playwright
import pandas as pd
import time

from config import *

AUTH_FILE = "linkedin_auth.json"


class LinkedInCollector:

    def __init__(self):
        self.jobs = []
        self.play = sync_playwright().start()
        self.browser = self.play.chromium.launch(headless=False)

        if os.path.exists(AUTH_FILE):
            # Reuse saved cookies/session — skips the login screen entirely.
            self.context = self.browser.new_context(storage_state=AUTH_FILE)
        else:
            self.context = self.browser.new_context()

        self.page = self.context.new_page()

    def login(self):
        # If we already loaded a saved session, verify it's still valid
        # before asking for a manual login again.
        if os.path.exists(AUTH_FILE):
            self.page.goto("https://www.linkedin.com/feed/")
            time.sleep(3)
            if "linkedin.com/feed" in self.page.url:
                print("Reusing saved session — skipping login.")
                return
            else:
                print("Saved session expired — please log in again.")

        self.page.goto("https://www.linkedin.com/login")
        print("=" * 60)
        print("Login manually.")
        print("Complete MFA if needed.")
        print("Then press ENTER.")
        print("=" * 60)
        input()

        # Persist cookies/local storage so future runs skip this step.
        self.context.storage_state(path=AUTH_FILE)
        print(f"Session saved to {AUTH_FILE}.")

    def safe_text(self, locator, default=""):
        """Return inner_text() or a default if the locator times out / has no match."""
        try:
            if locator.count() == 0:
                return default
            return locator.first.inner_text(timeout=5000).strip()
        except Exception:
            return default

    def collect_jobs(self):

        for keyword in SEARCH_TERMS:

            print(f"\nSearching {keyword}")

            # # url = (
            # #     "https://www.linkedin.com/jobs/search/"
            # #     f"?keywords={keyword.replace(' ', '%20')}"
            # # )
            # url = (
            #     "https://www.linkedin.com/jobs/search/"
            #     f"?keywords={keyword.replace(' ', '%20')}"
            #     "&f_TPR=r86400"
            #     "&sortBy=DD"
            # )
            url = (
                "https://www.linkedin.com/jobs/search/"
                f"?keywords={keyword.replace(' ', '%20')}"
                f"&f_TPR=r{POSTED_WITHIN}"
                "&sortBy=DD"
            )

            # self.page.goto(url)
            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=0,
            )
            time.sleep(5)

            for page_number in range(PAGES_TO_SCAN):

                print(f"Page {page_number + 1}")

                # LinkedIn lazy-loads job cards as you scroll — jumping straight
                # to the bottom skips the scroll events that trigger loading,
                # so only the first ~7 cards ever render. Scroll in smaller
                # increments with pauses so each batch has time to load.
                # LinkedIn lazy-loads job cards as you scroll — jumping straight
                # to the bottom skips the scroll events that trigger loading,
                # so only the first ~7 cards ever render. Rather than finding
                # the scroll container ourselves, just repeatedly scroll the
                # LAST currently-loaded card into view — Playwright's
                # scroll_into_view_if_needed automatically scrolls whatever
                # nested scrollable ancestor is needed, no selector required.
                previous_count = 0
                stable_rounds = 0

                # Position the mouse over the job list panel (left third of
                # the viewport, where LinkedIn renders it) so wheel events
                # actually land on that scrollable panel instead of the
                # page body. scroll_into_view_if_needed became a no-op once
                # the last card was already in view, so it stopped
                # triggering new loads after the first hit — real wheel
                # events don't have that problem.
                viewport = self.page.viewport_size or {"width": 1280, "height": 800}
                mouse_x = min(300, viewport["width"] * 0.25)
                mouse_y = viewport["height"] / 2
                self.page.mouse.move(mouse_x, mouse_y)

                for _ in range(40):
                    self.page.mouse.wheel(0, 800)

                    # LinkedIn fetches the next batch of cards via an API
                    # call after the scroll trigger fires — give it time
                    # for that round-trip before checking the count.
                    time.sleep(2)

                    current_count = self.page.locator(".job-card-container").count()

                    if current_count == previous_count:
                        stable_rounds += 1
                        if stable_rounds >= 5:
                            # No new cards after 5 consecutive scrolls — assume
                            # we've reached the end of this page's list.
                            break
                    else:
                        stable_rounds = 0

                    previous_count = current_count

                print(f"Loaded {previous_count} cards after scrolling.")

                cards = self.page.locator(".job-card-container").all()

                print(f"Found {len(cards)} cards")

                if not cards:
                    print("No job cards found on this page — selector may be stale.")

                for i, card in enumerate(cards):

                    # Defaults so a partial failure still produces a row
                    # instead of losing the card entirely.
                    title = ""
                    company = ""
                    location = ""
                    href = None
                    description = ""
                    posted = ""
                    applicants = ""
                    easy_apply = False

                    try:
                        # Scroll into view and click FIRST — clicking can
                        # change which card LinkedIn treats as "selected"
                        # and re-render its contents, and some fields
                        # (especially the description pane) aren't populated
                        # until after the click fires.
                        card.scroll_into_view_if_needed(timeout=5000)
                        card.click(timeout=5000)
                        time.sleep(2)

                        title = self.safe_text(card.locator("strong"))

                        # Fallback selectors — LinkedIn renames these classes often,
                        # so try a couple of variants instead of hard-failing.
                        company = self.safe_text(
                            card.locator(
                                ".artdeco-entity-lockup__subtitle, "
                                ".job-card-container__primary-description, "
                                ".job-card-container__company-name"
                            )
                        )

                        location = self.safe_text(
                            card.locator(
                                ".job-card-container__metadata-item, "
                                ".artdeco-entity-lockup__caption, "
                                "ul.job-card-container__metadata-wrapper li"
                            )
                        )

                        link_locator = card.locator("a").first
                        if link_locator.count():
                            raw_href = link_locator.get_attribute("href", timeout=5000)
                            if raw_href and raw_href.startswith("/"):
                                href = f"https://www.linkedin.com{raw_href}"
                            else:
                                href = raw_href

                        description = self.safe_text(
                            self.page.locator(
                                '[data-sdui-component="com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"], '
                                ".jobs-description__content, "
                                ".jobs-box__html-content"
                            )
                        )

                        metadata = self.safe_text(
                            self.page.locator(
                                ".job-details-jobs-unified-top-card__primary-description-container"
                            )
                        )

                        parts = [p.strip() for p in metadata.split("·")]

                        if len(parts) >= 1 and parts[0]:
                            location = parts[0]

                        if len(parts) >= 2:
                            posted = parts[1]

                        if len(parts) >= 3:
                            applicants = parts[2]

                        print(f"Metadata   : {metadata}")
                        print(f"Posted     : {posted}")
                        print(f"Applicants : {applicants}")
                        print(f"Easy Apply : {easy_apply}")
                        print("-" * 80)



                        easy_apply = (
                            self.page.locator("button:has-text('Easy Apply')").count() > 0
                        )

                        if description:
                            print("=" * 80)
                            print(description[:500000])
                            print("=" * 80)

                        print(f"  [{i+1}/{len(cards)}] {title or '(no title)'} @ {company or '(no company)'}")

                    except Exception as e:
                        print(f"Error on card {i+1}: {e}")
                        # Fall through — whatever fields were captured
                        # before the exception are still recorded below.

                    # self.jobs.append({
                    #     "Title": title,
                    #     "Company": company,
                    #     "Location": location,
                    #     "Description": description,
                    #     "URL": href,
                    #     "Keyword": keyword,
                    # })

                    self.jobs.append({
                        "Title": title,
                        "Company": company,
                        "Location": location,

                        "Posted": posted,
                        "Applicants": applicants,
                        "Easy Apply": easy_apply,

                        "Description": description,
                        "URL": href,
                        "Keyword": keyword,
                    })

                next_button = self.page.locator("button[aria-label='View next page']")

                if next_button.count():
                    try:
                        next_button.click(timeout=5000)
                        time.sleep(4)
                    except Exception as e:
                        print(f"Couldn't click next page: {e}")
                        break
                else:
                    break

    def save(self):
        df = pd.DataFrame(self.jobs)

        if df.empty:
            print("No jobs collected — nothing to save.")
            self.context.close()
            self.browser.close()
            self.play.stop()
            return

        df.drop_duplicates(subset=["URL"], inplace=True)
        df.to_csv(OUTPUT_CSV, index=False)

        print()
        print("=" * 60)
        print(f"Saved {len(df)} jobs.")
        print("=" * 60)

        self.context.close()
        self.browser.close()
        self.play.stop()