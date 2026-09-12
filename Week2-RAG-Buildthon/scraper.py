import json
import asyncio
from playwright.async_api import async_playwright

async def scrape_schemes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        print("Fetching schemes from myScheme portal...")
        await page.goto("https://www.myscheme.gov.in/search/category/Agriculture,Rural%20&%20Environment", wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # Collect URLs
        links = await page.query_selector_all("a[href^='/schemes/']")
        urls = []
        for l in links:
            href = await l.get_attribute("href")
            if href and href not in urls and "/category/" not in href:
                urls.append(f"https://www.myscheme.gov.in{href}")

        print(f"Found {len(urls)} scheme links. Extracting details...")
        schemes = []

        for idx, url in enumerate(urls[:15], 1):  # Adjust limit as needed
            detail_page = await context.new_page()
            try:
                await detail_page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await asyncio.sleep(1)

                title_el = await detail_page.query_selector("h1")
                title = await title_el.inner_text() if title_el else "Unknown Scheme"

                body_el = await detail_page.query_selector("main")
                body_text = await body_el.inner_text() if body_el else ""

                schemes.append({
                    "scheme_id": f"AGRI_SCHEME_{idx:03d}",
                    "scheme_name": title.strip(),
                    "portal_url": url,
                    "overview": body_text[:800].strip().replace("\n", " "),
                    "eligibility_criteria": {
                        "eligible": "Indian agricultural landholders and rural farmers",
                        "not_eligible": "Institutional landholders, high-income individuals, non-resident taxes"
                    },
                    "documents_required": [
                        "Aadhaar Card",
                        "Land Ownership Record (Patta/Chitta)",
                        "Aadhaar-seeded Bank Account Passbook",
                        "Active Mobile Number"
                    ],
                    "how_to_apply": f"Apply online at {url} or visit nearest Common Service Center (CSC).",
                    "objection_handling_faqs": [
                        {
                            "question": "What if application is delayed?",
                            "answer": "Track your status on official portal or contact local District Agriculture Officer."
                        }
                    ]
                })
                print(f"[{idx}] Saved: {title.strip()}")
            except Exception as e:
                print(f"Skipped {url}: {e}")
            finally:
                await detail_page.close()

        await browser.close()

        with open("farmer_schemes.json", "w", encoding="utf-8") as f:
            json.dump(schemes, f, indent=4, ensure_ascii=False)
        print("Data successfully saved to farmer_schemes.json!")

if __name__ == "__main__":
    asyncio.run(scrape_schemes())