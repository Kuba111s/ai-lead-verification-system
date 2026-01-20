import asyncio
from playwright.async_api import async_playwright
import openai
import pandas as pd
import nest_asyncio
import json

# Configuration
API_KEY = "YOUR_API_KEY_HERE"
nest_asyncio.apply()


# AI function
def ai_analysis(text):
    if not text or len(text) < 50:
        return None

    client = openai.OpenAI(api_key=API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an E-commerce Analyst. Output ONLY valid JSON."},
                {"role": "user", "content": f"""
                    Analyze this website text: "{text[:2500]}" 

                    Return a JSON object with:
                    1. "type": (Pick one: "E-commerce Store", "Blog", "Corporate Site", "Dead Link")
                    2. "is_store": (true/false)
                    3. "products": (List 2-3 main products sold, or "None")
                    4. "reasoning": (One short sentence why)
                    """}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return None


# Scraper
async def filter_leads():
    # List of URLs
    urls = [
        # <------ Add URLs HERE
    ]

    results = []
    print("Starting E-commerce Filter...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for url in urls:
            print(f"Checking {url}...")
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=15000)
                text = await page.inner_text("body")
                clean_text = " ".join(text.split())

                print("Analyzing...")
                raw_ai_text = ai_analysis(clean_text)

                if raw_ai_text:
                    # Clean up if AI adds markdown code blocks
                    clean_json = raw_ai_text.replace("```json", "").replace("```", "").strip()

                    try:
                        data = json.loads(clean_json)  # Convert text to Dictionary

                        # Handle the 'products' list cleanly
                        prod_list = data.get("products", [])
                        if isinstance(prod_list, list):
                            prod_str = ", ".join(prod_list)
                        else:
                            prod_str = str(prod_list)

                        results.append({
                            "URL": url,
                            "Type": data.get("type", "Unknown"),
                            "Is Store": "YES" if data.get("is_store") else "NO",
                            "Products": prod_str,
                            "Reasoning": data.get("reasoning", "")
                        })
                    except json.JSONDecodeError:
                        results.append({"URL": url, "Type": "AI Error", "Is Store": "Error", "Products": "",
                                        "Reasoning": "Invalid JSON returned"})
                else:
                    results.append({"URL": url, "Type": "Scrape Fail", "Is Store": "-", "Products": "-",
                                    "Reasoning": "Could not read text"})

            except Exception as e:
                print(f"Error: {e}")
                results.append({"URL": url, "Type": "Link Dead", "Is Store": "-", "Products": "-",
                                "Reasoning": "Site unreachable"})

            await page.close()

        await browser.close()

    # Excel formating
    filename = "ecommerce_leads_filtered.xlsx"
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    df = pd.DataFrame(results)

    # Write data starting at row 1 (leaving row 0 for our fancy header)
    df.to_excel(writer, sheet_name='Leads', index=False, startrow=1, header=False)

    workbook = writer.book
    worksheet = writer.sheets['Leads']

    # Styles
    header_fmt = workbook.add_format({
        'bold': True, 'fg_color': '#4F81BD', 'font_color': 'white', 'border': 1, 'valign': 'vcenter'
    })

    # Standard text
    body_fmt = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})

    # Write Headers
    headers = ["URL", "Type", "Is Store", "Products", "Reasoning"]
    for col_num, value in enumerate(headers):
        worksheet.write(0, col_num, value, header_fmt)

    # Set Column Widths
    worksheet.set_column('A:A', 40, body_fmt)  # URL
    worksheet.set_column('B:B', 20, body_fmt)  # Type
    worksheet.set_column('C:C', 15, body_fmt)  # Is Store
    worksheet.set_column('D:D', 30, body_fmt)  # Products
    worksheet.set_column('E:E', 50, body_fmt)  # Reasoning

    # Add Filters
    worksheet.autofilter(0, 0, len(df), 4)

    writer.close()
    print(f" Success! File saved as '{filename}'")

if __name__ == "__main__":
    asyncio.run(filter_leads())