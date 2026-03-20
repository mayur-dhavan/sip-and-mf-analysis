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
    _entry("120503", "Axis Small Cap Fund Direct Growth", "Axis Mutual Fund", "Small Cap", "0P0000XVKR.BO"),
    _entry("120834", "Axis Midcap Fund Direct Growth", "Axis Mutual Fund", "Mid Cap"),
    _entry("120716", "Axis Bluechip Fund Direct Growth", "Axis Mutual Fund", "Large Cap"),
    _entry("120861", "Axis Flexi Cap Fund Direct Growth", "Axis Mutual Fund", "Flexi Cap"),
    _entry("120866", "Axis ELSS Tax Saver Fund Direct Growth", "Axis Mutual Fund", "ELSS"),

    _entry("119551", "SBI Small Cap Fund Direct Growth", "SBI Mutual Fund", "Small Cap", "0P0000XVL1.BO"),
    _entry("119061", "SBI Bluechip Fund Direct Growth", "SBI Mutual Fund", "Large Cap"),
    _entry("118834", "SBI Contra Fund Direct Growth", "SBI Mutual Fund", "Contra"),
    _entry("119597", "SBI Focused Equity Fund Direct Growth", "SBI Mutual Fund", "Focused"),
    _entry("119068", "SBI Magnum Midcap Fund Direct Growth", "SBI Mutual Fund", "Mid Cap"),

    _entry("118989", "HDFC Small Cap Fund Direct Growth", "HDFC Mutual Fund", "Small Cap", "0P00013CZ6.BO"),
    _entry("118980", "HDFC Mid-Cap Opportunities Fund Direct Growth", "HDFC Mutual Fund", "Mid Cap"),
    _entry("118956", "HDFC Flexi Cap Fund Direct Growth", "HDFC Mutual Fund", "Flexi Cap"),
    _entry("1189891", "HDFC Balanced Advantage Fund Direct Growth", "HDFC Mutual Fund", "Dynamic Asset Allocation"),
    _entry("118964", "HDFC Index Fund Nifty 50 Plan Direct Growth", "HDFC Mutual Fund", "Index Fund"),

    _entry("120465", "Kotak Small Cap Fund Direct Growth", "Kotak Mutual Fund", "Small Cap", "0P0000XVKY.BO"),
    _entry("120090", "Kotak Emerging Equity Fund Direct Growth", "Kotak Mutual Fund", "Large and Mid Cap"),
    _entry("120443", "Kotak Equity Opportunities Fund Direct Growth", "Kotak Mutual Fund", "Large and Mid Cap"),
    _entry("120477", "Kotak Flexicap Fund Direct Growth", "Kotak Mutual Fund", "Flexi Cap"),
    _entry("120541", "Kotak Nifty 50 Index Fund Direct Growth", "Kotak Mutual Fund", "Index Fund"),

    _entry("120828", "Quant Small Cap Fund Direct Growth", "Quant Mutual Fund", "Small Cap", "0P0001BAP8.BO"),
    _entry("120825", "Quant Mid Cap Fund Direct Growth", "Quant Mutual Fund", "Mid Cap"),
    _entry("120814", "Quant Active Fund Direct Growth", "Quant Mutual Fund", "Multi Cap"),
    _entry("120811", "Quant Tax Plan Direct Growth", "Quant Mutual Fund", "ELSS"),
    _entry("120829", "Quant Flexi Cap Fund Direct Growth", "Quant Mutual Fund", "Flexi Cap"),

    _entry("1205031", "DSP Small Cap Fund Direct Growth", "DSP Mutual Fund", "Small Cap", "0P0000XVLR.BO"),
    _entry("120459", "DSP Midcap Fund Direct Growth", "DSP Mutual Fund", "Mid Cap"),
    _entry("120505", "DSP Flexi Cap Fund Direct Growth", "DSP Mutual Fund", "Flexi Cap"),
    _entry("120452", "DSP ELSS Tax Saver Fund Direct Growth", "DSP Mutual Fund", "ELSS"),
    _entry("120469", "DSP Nifty 50 Equal Weight Index Fund Direct Growth", "DSP Mutual Fund", "Index Fund"),

    _entry("118551", "ICICI Prudential Smallcap Fund Direct Growth", "ICICI Prudential Mutual Fund", "Small Cap", "0P0001BHGZ.BO"),
    _entry("118560", "ICICI Prudential Bluechip Fund Direct Growth", "ICICI Prudential Mutual Fund", "Large Cap"),
    _entry("1188341", "ICICI Prudential Value Discovery Fund Direct Growth", "ICICI Prudential Mutual Fund", "Value"),
    _entry("118607", "ICICI Prudential Balanced Advantage Fund Direct Growth", "ICICI Prudential Mutual Fund", "Dynamic Asset Allocation"),
    _entry("118732", "ICICI Prudential Nifty Index Fund Direct Growth", "ICICI Prudential Mutual Fund", "Index Fund"),

    _entry("122639", "Mirae Asset Large and Midcap Fund Direct Growth", "Mirae Asset Mutual Fund", "Large and Mid Cap", "0P0000XVKK.BO"),
    _entry("122640", "Mirae Asset Emerging Bluechip Fund Direct Growth", "Mirae Asset Mutual Fund", "Large and Mid Cap"),
    _entry("122641", "Mirae Asset Tax Saver Fund Direct Growth", "Mirae Asset Mutual Fund", "ELSS"),
    _entry("122642", "Mirae Asset Great Consumer Fund Direct Growth", "Mirae Asset Mutual Fund", "Sectoral"),
    _entry("122643", "Mirae Asset Large Cap Fund Direct Growth", "Mirae Asset Mutual Fund", "Large Cap"),

    _entry("122457", "Parag Parikh Flexi Cap Fund Direct Growth", "PPFAS Mutual Fund", "Flexi Cap", "0P0001K4CC.BO"),
    _entry("122458", "Parag Parikh ELSS Tax Saver Fund Direct Growth", "PPFAS Mutual Fund", "ELSS"),
    _entry("122459", "Parag Parikh Conservative Hybrid Fund Direct Growth", "PPFAS Mutual Fund", "Hybrid"),

    _entry("123456", "UTI Nifty 50 Index Fund Direct Growth", "UTI Mutual Fund", "Index Fund", "0P0000XV5N.BO"),
    _entry("123457", "UTI Flexi Cap Fund Direct Growth", "UTI Mutual Fund", "Flexi Cap"),
    _entry("123458", "UTI Mid Cap Fund Direct Growth", "UTI Mutual Fund", "Mid Cap"),
    _entry("123459", "UTI Nifty Next 50 Index Fund Direct Growth", "UTI Mutual Fund", "Index Fund"),

    _entry("124111", "Motilal Oswal Midcap Fund Direct Growth", "Motilal Oswal Mutual Fund", "Mid Cap", "0P0000XVGR.BO"),
    _entry("124112", "Motilal Oswal Nasdaq 100 FOF Direct Growth", "Motilal Oswal Mutual Fund", "International"),
    _entry("124113", "Motilal Oswal S&P 500 Index Fund Direct Growth", "Motilal Oswal Mutual Fund", "International"),
    _entry("124114", "Motilal Oswal Nifty Smallcap 250 Index Fund Direct Growth", "Motilal Oswal Mutual Fund", "Index Fund"),

    _entry("125001", "Canara Robeco Small Cap Fund Direct Growth", "Canara Robeco Mutual Fund", "Small Cap", "0P0000XVH2.BO"),
    _entry("125002", "Canara Robeco Bluechip Equity Fund Direct Growth", "Canara Robeco Mutual Fund", "Large Cap"),
    _entry("125003", "Canara Robeco Emerging Equities Fund Direct Growth", "Canara Robeco Mutual Fund", "Large and Mid Cap"),
    _entry("125004", "Canara Robeco Equity Tax Saver Fund Direct Growth", "Canara Robeco Mutual Fund", "ELSS"),

    _entry("126001", "Nippon India ETF Nifty BeES", "Nippon India Mutual Fund", "ETF", "NIPPONINDIA.NS"),
    _entry("126002", "Nippon India Small Cap Fund Direct Growth", "Nippon India Mutual Fund", "Small Cap"),
    _entry("126003", "Nippon India Growth Fund Direct Growth", "Nippon India Mutual Fund", "Mid Cap"),
    _entry("126004", "Nippon India Value Fund Direct Growth", "Nippon India Mutual Fund", "Value"),

    _entry("127001", "Aditya Birla Sun Life Small Cap Fund Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Small Cap"),
    _entry("127002", "Aditya Birla Sun Life Frontline Equity Fund Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Large Cap"),
    _entry("127003", "Aditya Birla Sun Life Equity Hybrid 95 Fund Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Aggressive Hybrid"),

    _entry("128001", "Franklin India Smaller Companies Fund Direct Growth", "Franklin Templeton Mutual Fund", "Small Cap"),
    _entry("128002", "Franklin India Flexi Cap Fund Direct Growth", "Franklin Templeton Mutual Fund", "Flexi Cap"),
    _entry("128003", "Franklin India ELSS Tax Saver Fund Direct Growth", "Franklin Templeton Mutual Fund", "ELSS"),

    _entry("129001", "Tata Small Cap Fund Direct Growth", "Tata Mutual Fund", "Small Cap"),
    _entry("129002", "Tata Digital India Fund Direct Growth", "Tata Mutual Fund", "Sectoral"),
    _entry("129003", "Tata Equity PE Fund Direct Growth", "Tata Mutual Fund", "Value"),

    _entry("130001", "Edelweiss Mid Cap Fund Direct Growth", "Edelweiss Mutual Fund", "Mid Cap"),
    _entry("130002", "Edelweiss Nifty Midcap 150 Momentum 50 Index Fund Direct Growth", "Edelweiss Mutual Fund", "Index Fund"),

    _entry("IDX001", "NIFTY 50 Index", "NSE Indices", "Benchmark Index", "^NSEI"),
    _entry("IDX002", "NIFTY Midcap 150 Index", "NSE Indices", "Benchmark Index", "^NSMIDCP"),
    _entry("IDX003", "NIFTY Bank Index", "NSE Indices", "Benchmark Index", "^NSEBANK"),
]
