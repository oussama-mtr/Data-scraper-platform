import pandas as pd

def load_companies():
    df = pd.read_csv('masi_companies.csv')
    return df

def screen_targets(sector_filter, max_ev_ebitda, min_revenue, min_roe, max_net_debt):
    df = load_companies()

    if sector_filter and sector_filter != 'All Sectors':
        df = df[df['sector'] == sector_filter]

    df = df[df['ev_ebitda'] <= max_ev_ebitda]
    df = df[df['revenue_mad_bn'] >= min_revenue]
    df = df[df['roe_pct'] >= min_roe]
    df = df[df['net_debt_mad_bn'] <= max_net_debt]

    df = df.copy()
    df['score'] = (
        (1 / df['ev_ebitda']) * 30 +
        df['roe_pct'] * 1.5 +
        df['revenue_growth_pct'] * 1.2 +
        (1 / (df['net_debt_mad_bn'] + 0.1)) * 5
    )

    df = df.sort_values('score', ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def get_sectors():
    df = load_companies()
    return ['All Sectors'] + sorted(df['sector'].unique().tolist())