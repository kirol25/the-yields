"""add tickers reference table, soft FK on dividend_entries, goals as integer

Revision ID: b4f812c9d1e2
Revises: 938beee1a35d
Create Date: 2026-03-20 21:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b4f812c9d1e2"
down_revision: str | None = "938beee1a35d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# ---------------------------------------------------------------------------
# Seed data — 100+ well-known dividend stocks and ETFs
# ---------------------------------------------------------------------------

TICKERS = [
    # US Technology
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corp.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "META",
        "name": "Meta Platforms Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corp.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "AVGO",
        "name": "Broadcom Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "TXN",
        "name": "Texas Instruments Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "INTC",
        "name": "Intel Corp.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "IBM",
        "name": "IBM Corp.",
        "sector": "Technology",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "CSCO",
        "name": "Cisco Systems Inc.",
        "sector": "Technology",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    # US Financials
    {
        "symbol": "JPM",
        "name": "JPMorgan Chase & Co.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "BAC",
        "name": "Bank of America Corp.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "WFC",
        "name": "Wells Fargo & Co.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "GS",
        "name": "Goldman Sachs Group Inc.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "MS",
        "name": "Morgan Stanley",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "BLK",
        "name": "BlackRock Inc.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "V",
        "name": "Visa Inc.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "MA",
        "name": "Mastercard Inc.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "AXP",
        "name": "American Express Co.",
        "sector": "Financials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Healthcare
    {
        "symbol": "JNJ",
        "name": "Johnson & Johnson",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "UNH",
        "name": "UnitedHealth Group Inc.",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "PFE",
        "name": "Pfizer Inc.",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "ABBV",
        "name": "AbbVie Inc.",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "MRK",
        "name": "Merck & Co. Inc.",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "ABT",
        "name": "Abbott Laboratories",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "MDT",
        "name": "Medtronic PLC",
        "sector": "Healthcare",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Consumer Staples
    {
        "symbol": "PG",
        "name": "Procter & Gamble Co.",
        "sector": "Consumer Staples",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "KO",
        "name": "Coca-Cola Co.",
        "sector": "Consumer Staples",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "PEP",
        "name": "PepsiCo Inc.",
        "sector": "Consumer Staples",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "COST",
        "name": "Costco Wholesale Corp.",
        "sector": "Consumer Staples",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "WMT",
        "name": "Walmart Inc.",
        "sector": "Consumer Staples",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "PM",
        "name": "Philip Morris International",
        "sector": "Consumer Staples",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "MO",
        "name": "Altria Group Inc.",
        "sector": "Consumer Staples",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "CL",
        "name": "Colgate-Palmolive Co.",
        "sector": "Consumer Staples",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Energy
    {
        "symbol": "XOM",
        "name": "Exxon Mobil Corp.",
        "sector": "Energy",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "CVX",
        "name": "Chevron Corp.",
        "sector": "Energy",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "COP",
        "name": "ConocoPhillips",
        "sector": "Energy",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "SLB",
        "name": "SLB (Schlumberger)",
        "sector": "Energy",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Industrials
    {
        "symbol": "HON",
        "name": "Honeywell International Inc.",
        "sector": "Industrials",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "MMM",
        "name": "3M Co.",
        "sector": "Industrials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "CAT",
        "name": "Caterpillar Inc.",
        "sector": "Industrials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "GE",
        "name": "GE Aerospace",
        "sector": "Industrials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "RTX",
        "name": "RTX Corp.",
        "sector": "Industrials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "UPS",
        "name": "United Parcel Service Inc.",
        "sector": "Industrials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "DE",
        "name": "Deere & Co.",
        "sector": "Industrials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Utilities
    {
        "symbol": "NEE",
        "name": "NextEra Energy Inc.",
        "sector": "Utilities",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "DUK",
        "name": "Duke Energy Corp.",
        "sector": "Utilities",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "SO",
        "name": "Southern Co.",
        "sector": "Utilities",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "D",
        "name": "Dominion Energy Inc.",
        "sector": "Utilities",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US REITs
    {
        "symbol": "O",
        "name": "Realty Income Corp.",
        "sector": "Real Estate",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "AMT",
        "name": "American Tower Corp.",
        "sector": "Real Estate",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "PLD",
        "name": "Prologis Inc.",
        "sector": "Real Estate",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "VICI",
        "name": "VICI Properties Inc.",
        "sector": "Real Estate",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Consumer Discretionary
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "sector": "Consumer Discretionary",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "HD",
        "name": "Home Depot Inc.",
        "sector": "Consumer Discretionary",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "MCD",
        "name": "McDonald's Corp.",
        "sector": "Consumer Discretionary",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "SBUX",
        "name": "Starbucks Corp.",
        "sector": "Consumer Discretionary",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "NKE",
        "name": "Nike Inc.",
        "sector": "Consumer Discretionary",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Communication Services
    {
        "symbol": "T",
        "name": "AT&T Inc.",
        "sector": "Communication Services",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "VZ",
        "name": "Verizon Communications Inc.",
        "sector": "Communication Services",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # US Materials
    {
        "symbol": "LIN",
        "name": "Linde PLC",
        "sector": "Materials",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "APD",
        "name": "Air Products & Chemicals Inc.",
        "sector": "Materials",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "NEM",
        "name": "Newmont Corp.",
        "sector": "Materials",
        "exchange": "NYSE",
        "currency": "USD",
    },
    # European — Germany (XETRA)
    {
        "symbol": "SAP",
        "name": "SAP SE",
        "sector": "Technology",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "SIE",
        "name": "Siemens AG",
        "sector": "Industrials",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "ALV",
        "name": "Allianz SE",
        "sector": "Financials",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "MBG",
        "name": "Mercedes-Benz Group AG",
        "sector": "Consumer Discretionary",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "BMW",
        "name": "Bayerische Motoren Werke AG",
        "sector": "Consumer Discretionary",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "VOW3",
        "name": "Volkswagen AG",
        "sector": "Consumer Discretionary",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "BAS",
        "name": "BASF SE",
        "sector": "Materials",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "BAYN",
        "name": "Bayer AG",
        "sector": "Healthcare",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "MUV2",
        "name": "Munich Re",
        "sector": "Financials",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "DTE",
        "name": "Deutsche Telekom AG",
        "sector": "Communication Services",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "DBK",
        "name": "Deutsche Bank AG",
        "sector": "Financials",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "DPW",
        "name": "Deutsche Post AG",
        "sector": "Industrials",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "RWE",
        "name": "RWE AG",
        "sector": "Utilities",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "EON",
        "name": "E.ON SE",
        "sector": "Utilities",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "HEN3",
        "name": "Henkel AG & Co. KGaA",
        "sector": "Consumer Staples",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "ADS",
        "name": "Adidas AG",
        "sector": "Consumer Discretionary",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "BEI",
        "name": "Beiersdorf AG",
        "sector": "Consumer Staples",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "FRE",
        "name": "Fresenius SE & Co. KGaA",
        "sector": "Healthcare",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "MRKDE",
        "name": "Merck KGaA",
        "sector": "Healthcare",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    # European — Other
    {
        "symbol": "NESN",
        "name": "Nestlé S.A.",
        "sector": "Consumer Staples",
        "exchange": "SIX",
        "currency": "CHF",
    },
    {
        "symbol": "NOVN",
        "name": "Novartis AG",
        "sector": "Healthcare",
        "exchange": "SIX",
        "currency": "CHF",
    },
    {
        "symbol": "ROG",
        "name": "Roche Holding AG",
        "sector": "Healthcare",
        "exchange": "SIX",
        "currency": "CHF",
    },
    {
        "symbol": "ASML",
        "name": "ASML Holding N.V.",
        "sector": "Technology",
        "exchange": "AMS",
        "currency": "EUR",
    },
    {
        "symbol": "RDSA",
        "name": "Shell PLC",
        "sector": "Energy",
        "exchange": "LSE",
        "currency": "GBP",
    },
    {
        "symbol": "HSBA",
        "name": "HSBC Holdings PLC",
        "sector": "Financials",
        "exchange": "LSE",
        "currency": "GBP",
    },
    {
        "symbol": "BP",
        "name": "BP PLC",
        "sector": "Energy",
        "exchange": "LSE",
        "currency": "GBP",
    },
    {
        "symbol": "GSK",
        "name": "GSK PLC",
        "sector": "Healthcare",
        "exchange": "LSE",
        "currency": "GBP",
    },
    {
        "symbol": "AZN",
        "name": "AstraZeneca PLC",
        "sector": "Healthcare",
        "exchange": "LSE",
        "currency": "GBP",
    },
    {
        "symbol": "ULVR",
        "name": "Unilever PLC",
        "sector": "Consumer Staples",
        "exchange": "LSE",
        "currency": "GBP",
    },
    {
        "symbol": "LVMH",
        "name": "LVMH Moët Hennessy SA",
        "sector": "Consumer Discretionary",
        "exchange": "EPA",
        "currency": "EUR",
    },
    {
        "symbol": "TTE",
        "name": "TotalEnergies SE",
        "sector": "Energy",
        "exchange": "EPA",
        "currency": "EUR",
    },
    {
        "symbol": "BNP",
        "name": "BNP Paribas SA",
        "sector": "Financials",
        "exchange": "EPA",
        "currency": "EUR",
    },
    # ETFs
    {
        "symbol": "VYM",
        "name": "Vanguard High Dividend Yield ETF",
        "sector": "ETF",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "SCHD",
        "name": "Schwab US Dividend Equity ETF",
        "sector": "ETF",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "DVY",
        "name": "iShares Select Dividend ETF",
        "sector": "ETF",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "JEPI",
        "name": "JPMorgan Equity Premium Income ETF",
        "sector": "ETF",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "JEPQ",
        "name": "JPMorgan Nasdaq Equity Premium Income ETF",
        "sector": "ETF",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "QYLD",
        "name": "Global X Nasdaq 100 Covered Call ETF",
        "sector": "ETF",
        "exchange": "NASDAQ",
        "currency": "USD",
    },
    {
        "symbol": "DIVO",
        "name": "Amplify CWP Enhanced Dividend Income ETF",
        "sector": "ETF",
        "exchange": "NYSE",
        "currency": "USD",
    },
    {
        "symbol": "EXW1",
        "name": "iShares Core MSCI World UCITS ETF",
        "sector": "ETF",
        "exchange": "XETRA",
        "currency": "EUR",
    },
    {
        "symbol": "VWRL",
        "name": "Vanguard FTSE All-World UCITS ETF",
        "sector": "ETF",
        "exchange": "AMS",
        "currency": "USD",
    },
    {
        "symbol": "ISPA",
        "name": "iShares STOXX Global Select Dividend ETF",
        "sector": "ETF",
        "exchange": "XETRA",
        "currency": "EUR",
    },
]


def upgrade() -> None:
    op.create_table(
        "tickers",
        sa.Column("symbol", sa.String(20), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sector", sa.String(100), nullable=True),
        sa.Column("exchange", sa.String(20), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
    )

    tickers_table = sa.table(
        "tickers",
        sa.column("symbol", sa.String),
        sa.column("name", sa.String),
        sa.column("sector", sa.String),
        sa.column("exchange", sa.String),
        sa.column("currency", sa.String),
    )
    op.bulk_insert(tickers_table, TICKERS)

    # Soft FK from dividend_entries to tickers (nullable — allows custom symbols)
    op.add_column(
        "dividend_entries",
        sa.Column(
            "ticker_symbol",
            sa.String(20),
            sa.ForeignKey("tickers.symbol", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_dividend_entries_ticker_symbol",
        "dividend_entries",
        ["ticker_symbol"],
    )

    # Make dividend_entries.name nullable (display name override,
    # falls back to tickers.name)
    op.alter_column("dividend_entries", "name", nullable=True)

    # Change year_goals goal columns from NUMERIC(12,4) to INTEGER
    op.alter_column(
        "year_goals",
        "dividend_goal",
        type_=sa.Integer(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
        postgresql_using="dividend_goal::integer",
    )
    op.alter_column(
        "year_goals",
        "yield_goal",
        type_=sa.Integer(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
        postgresql_using="yield_goal::integer",
    )
    op.alter_column(
        "year_goals",
        "steuerfreibetrag",
        type_=sa.Integer(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
        postgresql_using="steuerfreibetrag::integer",
    )


def downgrade() -> None:
    op.alter_column(
        "year_goals",
        "steuerfreibetrag",
        type_=sa.Numeric(12, 4),
        existing_type=sa.Integer(),
        existing_nullable=True,
        postgresql_using="steuerfreibetrag::numeric",
    )
    op.alter_column(
        "year_goals",
        "yield_goal",
        type_=sa.Numeric(12, 4),
        existing_type=sa.Integer(),
        existing_nullable=True,
        postgresql_using="yield_goal::numeric",
    )
    op.alter_column(
        "year_goals",
        "dividend_goal",
        type_=sa.Numeric(12, 4),
        existing_type=sa.Integer(),
        existing_nullable=True,
        postgresql_using="dividend_goal::numeric",
    )
    op.alter_column("dividend_entries", "name", nullable=False)
    op.drop_index("ix_dividend_entries_ticker_symbol", table_name="dividend_entries")
    op.drop_column("dividend_entries", "ticker_symbol")
    op.drop_table("tickers")
