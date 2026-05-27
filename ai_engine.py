import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def generate_ma_rationale(acquirer_profile, target_row):
    prompt = (
        "You are a senior M&A analyst specializing in Moroccan and African markets.\n\n"
        "ACQUIRER PROFILE:\n"
        "- Industry: " + str(acquirer_profile['industry']) + "\n"
        "- Strategic Goal: " + str(acquirer_profile['goal']) + "\n"
        "- Budget (MAD Bn): " + str(acquirer_profile['budget']) + "\n"
        "- Key Priorities: " + str(acquirer_profile['priorities']) + "\n\n"
        "TARGET COMPANY:\n"
        "- Name: " + str(target_row['name']) + "\n"
        "- Sector: " + str(target_row['sector']) + "\n"
        "- Market Cap: " + str(target_row['market_cap_mad_bn']) + " Bn MAD\n"
        "- Revenue: " + str(target_row['revenue_mad_bn']) + " Bn MAD\n"
        "- EV/EBITDA: " + str(target_row['ev_ebitda']) + "x\n"
        "- ROE: " + str(target_row['roe_pct']) + "%\n"
        "- Revenue Growth: " + str(target_row['revenue_growth_pct']) + "%\n"
        "- Net Debt: " + str(target_row['net_debt_mad_bn']) + " Bn MAD\n\n"
        "Write a professional 3-paragraph acquisition rationale with these sections:\n"
        "1. STRATEGIC FIT\n"
        "2. FINANCIAL ATTRACTIVENESS\n"
        "3. KEY RISKS\n"
        "Write in a professional investment banking style. Be specific and use the numbers provided."
    )

    message = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=600,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return message.content[0].text


def summarize_deal(article_title, article_content, article_url):
    prompt = (
        "You are an M&A analyst covering African and Moroccan markets.\n\n"
        "Analyze this news article:\n\n"
        "TITLE: " + str(article_title) + "\n"
        "CONTENT: " + str(article_content)[:1500] + "\n\n"
        "Extract and present the following:\n"
        "- DEAL SUMMARY\n"
        "- PARTIES\n"
        "- SECTOR\n"
        "- ESTIMATED VALUE\n"
        "- GEOGRAPHIC FOCUS\n"
        "- STRATEGIC RATIONALE\n"
        "- SIGNIFICANCE FOR AFRICAN MARKETS\n\n"
        "If this is NOT an M&A deal, respond with exactly: NOT_MA_DEAL"
    )

    message = client.messages.create(
        model='claude-sonnet-4-20250514',
        max_tokens=500,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return message.content[0].text