"""AMFI-style mutual fund master list used for search and symbol lookup UX.

This registry is intentionally broader than the set of symbols currently supported
for model inference. Entries with a mapped Yahoo ticker can be analyzed directly.
"""

from typing import List, Dict, Optional


def _entry(
    amfi_code: str,
    name: str,
    fund_house: str,
    category: str,
    yahoo_ticker: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    return {
        "amfi_code": amfi_code,
        "name": name,
        "fund_house": fund_house,
        "category": category,
        "yahoo_ticker": yahoo_ticker,
    }


AMFI_MASTER_FUNDS: List[Dict[str, Optional[str]]] = [
    # --- Axis Mutual Fund ---
    _entry("120503", "Axis Small Cap Fund Direct Growth", "Axis Mutual Fund", "Small Cap", "0P0000XVKR.BO"),
    _entry("120834", "Axis Midcap Fund Direct Growth", "Axis Mutual Fund", "Mid Cap", "0P0000XVKS.BO"),
    _entry("120716", "Axis Bluechip Fund Direct Growth", "Axis Mutual Fund", "Large Cap", "0P0000XVKN.BO"),
    _entry("120861", "Axis Flexi Cap Fund Direct Growth", "Axis Mutual Fund", "Flexi Cap", "0P0000XVKT.BO"),
    _entry("120866", "Axis ELSS Tax Saver Fund Direct Growth", "Axis Mutual Fund", "ELSS", "0P0000XVKU.BO"),

    # --- SBI Mutual Fund ---
    _entry("125497", "SBI Small Cap Fund Direct Growth", "SBI Mutual Fund", "Small Cap", "0P0000XVL1.BO"),
    _entry("119041", "SBI Bluechip Fund Direct Growth", "SBI Mutual Fund", "Large Cap", "0P0000XVKX.BO"),
    _entry("118834", "SBI Contra Fund Direct Growth", "SBI Mutual Fund", "Contra"),
    _entry("119597", "SBI Focused Equity Fund Direct Growth", "SBI Mutual Fund", "Focused"),
    _entry("125494", "SBI Magnum Midcap Fund Direct Growth", "SBI Mutual Fund", "Mid Cap", "0P0000XVKZ.BO"),
    _entry("119598", "SBI Equity Hybrid Fund Direct Growth", "SBI Mutual Fund", "Aggressive Hybrid"),
    _entry("120847", "SBI Long Term Equity Fund Direct Growth", "SBI Mutual Fund", "ELSS"),

    # --- HDFC Mutual Fund ---
    _entry("118989", "HDFC Small Cap Fund Direct Growth", "HDFC Mutual Fund", "Small Cap", "0P00013CZ6.BO"),
    _entry("118980", "HDFC Mid-Cap Opportunities Fund Direct Growth", "HDFC Mutual Fund", "Mid Cap", "0P0000XVAX.BO"),
    _entry("118956", "HDFC Flexi Cap Fund Direct Growth", "HDFC Mutual Fund", "Flexi Cap", "0P0000XVAT.BO"),
    _entry("119089", "HDFC Balanced Advantage Fund Direct Growth", "HDFC Mutual Fund", "Dynamic Asset Allocation", "0P0000XVAV.BO"),
    _entry("118964", "HDFC Index Fund Nifty 50 Plan Direct Growth", "HDFC Mutual Fund", "Index Fund"),
    _entry("118955", "HDFC Top 100 Fund Direct Growth", "HDFC Mutual Fund", "Large Cap", "0P0000XVAR.BO"),

    # --- Kotak Mutual Fund ---
    _entry("120465", "Kotak Small Cap Fund Direct Growth", "Kotak Mutual Fund", "Small Cap", "0P0000XVKY.BO"),
    _entry("120090", "Kotak Emerging Equity Fund Direct Growth", "Kotak Mutual Fund", "Large and Mid Cap", "0P0000XVKV.BO"),
    _entry("120443", "Kotak Equity Opportunities Fund Direct Growth", "Kotak Mutual Fund", "Large and Mid Cap", "0P0000XVKW.BO"),
    _entry("120477", "Kotak Flexicap Fund Direct Growth", "Kotak Mutual Fund", "Flexi Cap"),
    _entry("120541", "Kotak Nifty 50 Index Fund Direct Growth", "Kotak Mutual Fund", "Index Fund"),

    # --- Quant Mutual Fund ---
    _entry("120828", "Quant Small Cap Fund Direct Growth", "Quant Mutual Fund", "Small Cap", "0P0001BAP8.BO"),
    _entry("120825", "Quant Mid Cap Fund Direct Growth", "Quant Mutual Fund", "Mid Cap", "0P0001BAP6.BO"),
    _entry("120814", "Quant Active Fund Direct Growth", "Quant Mutual Fund", "Multi Cap", "0P0001BAP3.BO"),
    _entry("120811", "Quant Tax Plan Direct Growth", "Quant Mutual Fund", "ELSS"),
    _entry("120829", "Quant Flexi Cap Fund Direct Growth", "Quant Mutual Fund", "Flexi Cap", "0P0001BAP9.BO"),

    # --- DSP Mutual Fund ---
    _entry("119019", "DSP Small Cap Fund Direct Growth", "DSP Mutual Fund", "Small Cap", "0P0000XVLR.BO"),
    _entry("119018", "DSP Midcap Fund Direct Growth", "DSP Mutual Fund", "Mid Cap", "0P0000XVLQ.BO"),
    _entry("119017", "DSP Flexi Cap Fund Direct Growth", "DSP Mutual Fund", "Flexi Cap", "0P0000XVLP.BO"),
    _entry("119020", "DSP ELSS Tax Saver Fund Direct Growth", "DSP Mutual Fund", "ELSS", "0P0000XVLS.BO"),
    _entry("119022", "DSP Nifty 50 Equal Weight Index Fund Direct Growth", "DSP Mutual Fund", "Index Fund"),

    # --- ICICI Prudential Mutual Fund ---
    _entry("120586", "ICICI Prudential Smallcap Fund Direct Growth", "ICICI Prudential Mutual Fund", "Small Cap", "0P0001BHGZ.BO"),
    _entry("120175", "ICICI Prudential Bluechip Fund Direct Growth", "ICICI Prudential Mutual Fund", "Large Cap", "0P0000XVJT.BO"),
    _entry("120331", "ICICI Prudential Value Discovery Fund Direct Growth", "ICICI Prudential Mutual Fund", "Value", "0P0000XVJY.BO"),
    _entry("120177", "ICICI Prudential Balanced Advantage Fund Direct Growth", "ICICI Prudential Mutual Fund", "Dynamic Asset Allocation", "0P0000XVJU.BO"),
    _entry("120232", "ICICI Prudential Nifty 50 Index Fund Direct Growth", "ICICI Prudential Mutual Fund", "Index Fund"),
    _entry("120594", "ICICI Prudential Technology Fund Direct Growth", "ICICI Prudential Mutual Fund", "Sectoral", "0P0000XVJX.BO"),

    # --- Mirae Asset Mutual Fund ---
    _entry("118834", "Mirae Asset Large and Midcap Fund Direct Growth", "Mirae Asset Mutual Fund", "Large and Mid Cap", "0P0000XVKK.BO"),
    _entry("118835", "Mirae Asset Emerging Bluechip Fund Direct Growth", "Mirae Asset Mutual Fund", "Large and Mid Cap"),
    _entry("118836", "Mirae Asset Tax Saver Fund Direct Growth", "Mirae Asset Mutual Fund", "ELSS", "0P0000XVKL.BO"),
    _entry("118837", "Mirae Asset Great Consumer Fund Direct Growth", "Mirae Asset Mutual Fund", "Sectoral"),
    _entry("118838", "Mirae Asset Large Cap Fund Direct Growth", "Mirae Asset Mutual Fund", "Large Cap", "0P0000XVKJ.BO"),

    # --- PPFAS Mutual Fund ---
    _entry("122639", "Parag Parikh Flexi Cap Fund Direct Growth", "PPFAS Mutual Fund", "Flexi Cap", "0P0001K4CC.BO"),
    _entry("122640", "Parag Parikh ELSS Tax Saver Fund Direct Growth", "PPFAS Mutual Fund", "ELSS"),
    _entry("122641", "Parag Parikh Conservative Hybrid Fund Direct Growth", "PPFAS Mutual Fund", "Hybrid"),

    # --- UTI Mutual Fund ---
    _entry("120716", "UTI Nifty 50 Index Fund Direct Growth", "UTI Mutual Fund", "Index Fund", "0P0000XV5N.BO"),
    _entry("120211", "UTI Flexi Cap Fund Direct Growth", "UTI Mutual Fund", "Flexi Cap", "0P0000XVKE.BO"),
    _entry("120213", "UTI Mid Cap Fund Direct Growth", "UTI Mutual Fund", "Mid Cap"),
    _entry("120718", "UTI Nifty Next 50 Index Fund Direct Growth", "UTI Mutual Fund", "Index Fund"),

    # --- Motilal Oswal Mutual Fund ---
    _entry("119770", "Motilal Oswal Midcap Fund Direct Growth", "Motilal Oswal Mutual Fund", "Mid Cap", "0P0000XVGR.BO"),
    _entry("119771", "Motilal Oswal Nasdaq 100 FOF Direct Growth", "Motilal Oswal Mutual Fund", "International", "0P0001BKBQ.BO"),
    _entry("145082", "Motilal Oswal S&P 500 Index Fund Direct Growth", "Motilal Oswal Mutual Fund", "International"),
    _entry("145083", "Motilal Oswal Nifty Smallcap 250 Index Fund Direct Growth", "Motilal Oswal Mutual Fund", "Index Fund"),

    # --- Canara Robeco Mutual Fund ---
    _entry("114472", "Canara Robeco Small Cap Fund Direct Growth", "Canara Robeco Mutual Fund", "Small Cap", "0P0000XVH2.BO"),
    _entry("114471", "Canara Robeco Bluechip Equity Fund Direct Growth", "Canara Robeco Mutual Fund", "Large Cap", "0P0000XVH1.BO"),
    _entry("114473", "Canara Robeco Emerging Equities Fund Direct Growth", "Canara Robeco Mutual Fund", "Large and Mid Cap", "0P0000XVH3.BO"),
    _entry("114474", "Canara Robeco Equity Tax Saver Fund Direct Growth", "Canara Robeco Mutual Fund", "ELSS"),

    # --- Nippon India Mutual Fund ---
    _entry("118778", "Nippon India ETF Nifty BeES", "Nippon India Mutual Fund", "ETF", "NIFTYBEES.NS"),
    _entry("118750", "Nippon India Small Cap Fund Direct Growth", "Nippon India Mutual Fund", "Small Cap", "0P0000XVGE.BO"),
    _entry("118688", "Nippon India Growth Fund Direct Growth", "Nippon India Mutual Fund", "Mid Cap", "0P0000XVGB.BO"),
    _entry("118690", "Nippon India Value Fund Direct Growth", "Nippon India Mutual Fund", "Value"),
    _entry("118701", "Nippon India Large Cap Fund Direct Growth", "Nippon India Mutual Fund", "Large Cap", "0P0000XVGD.BO"),

    # --- Aditya Birla Sun Life Mutual Fund ---
    _entry("120503", "Aditya Birla SL Small Cap Fund Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Small Cap"),
    _entry("119591", "Aditya Birla SL Frontline Equity Fund Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Large Cap", "0P0000XVHA.BO"),
    _entry("119592", "Aditya Birla SL Equity Hybrid 95 Fund Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Aggressive Hybrid"),

    # --- Franklin Templeton Mutual Fund ---
    _entry("118485", "Franklin India Smaller Companies Fund Direct Growth", "Franklin Templeton Mutual Fund", "Small Cap", "0P0000XVG4.BO"),
    _entry("118487", "Franklin India Flexi Cap Fund Direct Growth", "Franklin Templeton Mutual Fund", "Flexi Cap", "0P0000XVG5.BO"),
    _entry("118486", "Franklin India ELSS Tax Saver Fund Direct Growth", "Franklin Templeton Mutual Fund", "ELSS"),

    # --- Tata Mutual Fund ---
    _entry("119306", "Tata Small Cap Fund Direct Growth", "Tata Mutual Fund", "Small Cap"),
    _entry("119307", "Tata Digital India Fund Direct Growth", "Tata Mutual Fund", "Sectoral", "0P0000XVK1.BO"),
    _entry("119308", "Tata Equity PE Fund Direct Growth", "Tata Mutual Fund", "Value"),

    # --- Edelweiss Mutual Fund ---
    _entry("119767", "Edelweiss Mid Cap Fund Direct Growth", "Edelweiss Mutual Fund", "Mid Cap"),
    _entry("119768", "Edelweiss Nifty Midcap 150 Momentum 50 Index Fund Direct Growth", "Edelweiss Mutual Fund", "Index Fund"),

    # --- Bandhan Mutual Fund ---
    _entry("119455", "Bandhan Small Cap Fund Direct Growth", "Bandhan Mutual Fund", "Small Cap"),
    _entry("119456", "Bandhan Flexi Cap Fund Direct Growth", "Bandhan Mutual Fund", "Flexi Cap"),

    # --- PGIM India Mutual Fund ---
    _entry("144901", "PGIM India Midcap Opportunities Fund Direct Growth", "PGIM India Mutual Fund", "Mid Cap"),
    _entry("144902", "PGIM India Flexi Cap Fund Direct Growth", "PGIM India Mutual Fund", "Flexi Cap"),

    # --- Benchmark Indices ---
    _entry("IDX001", "NIFTY 50 Index", "NSE Indices", "Benchmark Index", "^NSEI"),
    _entry("IDX002", "NIFTY Midcap 150 Index", "NSE Indices", "Benchmark Index", "^NSMIDCP"),
    _entry("IDX003", "NIFTY Bank Index", "NSE Indices", "Benchmark Index", "^NSEBANK"),
    _entry("IDX004", "SENSEX / BSE 30 Index", "BSE Indices", "Benchmark Index", "^BSESN"),
    _entry("IDX005", "NIFTY IT Index", "NSE Indices", "Benchmark Index", "^CNXIT"),
]
