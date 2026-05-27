import streamlit as st
from screener import screen_targets, get_sectors
from ai_engine import generate_ma_rationale, summarize_deal
from news_tracker import fetch_ma_deals

st.set_page_config(
    page_title='AI Finance Platform | Oussama Matrouf',
    layout='wide'
)

st.sidebar.title('M&Ai Finance Platform')
st.sidebar.markdown('**Mohammed Oussama Matrouf**')
st.sidebar.markdown('ENCG Casablanca')
st.sidebar.divider()

page = st.sidebar.radio(
    'Navigate to:',
    ['M&A Target Screener', 'African Deal Tracker', 'About']
)

st.sidebar.divider()
st.sidebar.caption('Powered by Claude AI (Anthropic)')

# PAGE 1: M&A SCREENER
if page == 'M&A Target Screener':
    st.title('AI-Powered M&A Target Screener')
    st.markdown('Enter an acquirer profile and AI screens the MASI universe for the best targets.')
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Acquirer Profile')
        industry = st.text_input('Acquirer Industry', placeholder='e.g. Banking, Telecom...')
        goal = st.text_input('Strategic Goal', placeholder='e.g. Geographic expansion...')
        budget = st.number_input('Max Budget (MAD Billions)', min_value=0.1, max_value=200.0, value=15.0)
        priorities = st.text_area('Key Priorities', placeholder='e.g. Strong brand, low debt...')

    with col2:
        st.subheader('Financial Filters')
        sector_filter = st.selectbox('Target Sector', get_sectors())
        max_ev_ebitda = st.slider('Max EV/EBITDA', 4.0, 30.0, 15.0, 0.5)
        min_revenue = st.slider('Min Revenue (MAD Bn)', 0.0, 20.0, 1.0, 0.5)
        min_roe = st.slider('Min ROE (%)', 0.0, 30.0, 8.0, 0.5)
        max_net_debt = st.slider('Max Net Debt (MAD Bn)', 0.0, 30.0, 10.0, 0.5)

    st.divider()
    run_btn = st.button('Run AI Screening', type='primary', use_container_width=True)

    if run_btn:
        if not industry or not goal:
            st.warning('Please fill in the Acquirer Industry and Strategic Goal fields.')
        else:
            with st.spinner('Screening MASI companies...'):
                acquirer = {
                    'industry': industry,
                    'goal': goal,
                    'budget': budget,
                    'priorities': priorities
                }
                results = screen_targets(sector_filter, max_ev_ebitda, min_revenue, min_roe, max_net_debt)

            if results.empty:
                st.error('No companies match your criteria. Try relaxing your filters.')
            else:
                st.success('Found ' + str(len(results)) + ' matching companies.')
                display_cols = ['name', 'sector', 'market_cap_mad_bn', 'ev_ebitda', 'roe_pct', 'revenue_growth_pct']
                st.dataframe(results[display_cols].head(10), use_container_width=True)

                st.subheader('AI Acquisition Rationale - Top 3 Targets')
                for i, (_, row) in enumerate(results.head(3).iterrows(), 1):
                    with st.expander('#' + str(i) + ' - ' + str(row['name']) + ' | EV/EBITDA: ' + str(row['ev_ebitda']) + 'x'):
                        with st.spinner('Generating rationale for ' + str(row['name']) + '...'):
                            rationale = generate_ma_rationale(acquirer, row)
                        st.markdown(rationale)

# PAGE 2: DEAL TRACKER
elif page == 'African Deal Tracker':
    st.title('African & Moroccan M&A Deal Tracker')
    st.markdown('Real-time AI-powered intelligence on M&A activity across Africa and Morocco.')
    st.divider()

    days_back = st.slider('News from the last N days:', 7, 60, 30)
    fetch_btn = st.button('Fetch & Analyze Deals', type='primary')

    if fetch_btn:
        with st.spinner('Fetching latest M&A news from Africa...'):
            articles = fetch_ma_deals(days_back=days_back)

        if not articles:
            st.warning('No articles found. Check your NewsAPI key in the .env file.')
        else:
            deal_count = 0
            for article in articles:
                combined = article['description'] + ' ' + article['content']
                with st.spinner('Analyzing: ' + article['title'][:50] + '...'):
                    analysis = summarize_deal(article['title'], combined, article['url'])

                if analysis.strip() == 'NOT_MA_DEAL':
                    continue

                deal_count += 1
                label = 'Deal #' + str(deal_count) + ' - ' + article['title'][:70] + ' | ' + article['source'] + ' | ' + article['published_at']
                with st.expander(label):
                    st.markdown(analysis)
                    st.caption('Source: ' + article['source'] + ' — ' + article['url'])

            if deal_count == 0:
                st.warning('No M&A deals identified. Try a wider date range.')
            else:
                st.success('Done. ' + str(deal_count) + ' M&A deals identified and analyzed.')

# PAGE 3: ABOUT
elif page == 'About':
    st.title('About This Platform')
    st.markdown('''
## AI Finance Platform
**Built by Mohammed Oussama Matrouf**
 | ENCG Casablanca

### Features
**1. M&A Target Screener** — Screens the MASI universe with AI-generated acquisition rationales.

**2. African Deal Tracker** — Real-time M&A news aggregation and AI deal analysis.

### Stack
Python + Streamlit + Claude AI (Anthropic) + NewsAPI
    ''')