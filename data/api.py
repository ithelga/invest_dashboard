import asyncio
import pandas as pd
from tinkoff.invest import AsyncClient, InstrumentIdType
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('API_TOKEN')
instrument_cache = {}

def get_manual_sector(ticker, instrument_type, instrument_name):
    if instrument_type == 'etf':
        return 'Смешанный'
    elif instrument_type == 'bond' and 'ОФЗ' in instrument_name:
        return 'Государственный'
    elif instrument_type == 'share':
        sectors = {
            'Нефтегазовый': ['LKOH', 'ROSN', 'NVTK', 'GAZP', 'SIBN', 'SNGSP', 'TATNP'],
            'Электроэнергетика': ['FEES', 'UPRO', 'HYDR'],
            'Финансовый': ['MOEX', 'SBER', 'SBERP', 'T', 'VTBR'],
            'Металлургический': ['CHMF', 'TRMK', 'ALRS', 'MAGN', 'NLMK'],
            'Телекоммуникаций': ['MTSS', 'RTKM', 'RTKMP'],
            'Химический': ['PHOR', 'NKNC', 'NKNCP'],
            'Золотодобытчиков': ['PLZL'],
            'Строительный': ['PIKK', 'ETLN'],
            'Потребительский': ['MGNT', 'MVID', 'LSRG', 'OZON'],
            'Транспортный': ['FLOT', 'NMTP', 'FIVE', 'AGRO'],
            'Здравоохранения': ['MDMG'],
            'ИТ': ['YDEX']
        }
        for sector, tickers in sectors.items():
            if ticker in tickers:
                return sector
    return 'Другое'


def calculate_amount(units, nano):
    return units + nano / 1_000_000_000


async def get_instrument_info_safe(client, figi, retries=3, delay=5):
    if figi in instrument_cache:
        return instrument_cache[figi]
    for attempt in range(retries):
        try:
            instrument_info = await client.instruments.get_instrument_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                id=figi
            )
            instrument_cache[figi] = instrument_info
            return instrument_info
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                print(f"Лимит запросов исчерпан, попытка {attempt + 1}/{retries}, ждем {delay} секунд")
                await asyncio.sleep(delay)
            else:
                raise e
    raise RuntimeError(f"Не удалось получить данные для FIGI {figi} после {retries} попыток")


async def main():
    async with AsyncClient(TOKEN) as client:
        accounts = await client.users.get_accounts()
        operations_data = []
        portfolio_data = []

        for account in accounts.accounts:
            if account.id != '2095107625':
                print(f"Название счета: {account.name}")

                operations = await client.operations.get_operations(account_id=account.id)
                for operation in operations.operations:
                    operations_data.append({
                        'date': operation.date,
                        'portfolio_id': account.id,
                        'portfolio_name': account.name,
                        'currency': operation.payment.currency,
                        'amount': abs(calculate_amount(operation.payment.units, operation.payment.nano)),
                        'type': operation.type,
                    })

                portfolio = await client.operations.get_portfolio(account_id=account.id)
                for position in portfolio.positions:
                    figi = position.figi
                    if not figi:
                        print(f"Пропущена позиция без FIGI: {position}")
                        continue

                    instrument_type = position.instrument_type
                    quantity = calculate_amount(position.quantity.units, position.quantity.nano)
                    average_price = calculate_amount(position.average_position_price.units,
                                                     position.average_position_price.nano)
                    current_price = calculate_amount(position.current_price.units, position.current_price.nano)
                    expected_yield = calculate_amount(position.expected_yield.units, position.expected_yield.nano)

                    try:
                        instrument_info = await get_instrument_info_safe(client, figi)
                    except Exception as e:
                        print(f"Ошибка при получении информации об инструменте {figi}: {e}")
                        continue

                    ticker = instrument_info.instrument.ticker if instrument_info.instrument else None
                    isin = instrument_info.instrument.isin if instrument_info.instrument else "Другое"
                    instrument_name = instrument_info.instrument.name if instrument_info.instrument else "Другое"

                    sector = get_manual_sector(ticker, instrument_type, instrument_name)

                    portfolio_data.append({
                        'portfolio_id': account.id,
                        'portfolio_name': account.name,
                        'isin': isin,
                        'ticker': ticker,
                        'name': instrument_name,
                        'type': instrument_type,
                        'sector': sector,
                        'quantity': quantity,
                        'average_price': average_price,
                        'current_price': current_price,
                        'expected_yield': expected_yield,
                    })

        portfolio_df = pd.DataFrame(portfolio_data)
        operations_df = pd.DataFrame(operations_data)

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', None)

        portfolio_df.to_csv('portfolio.csv', index=False)
        operations_df.to_csv('operations.csv', index=False)


if __name__ == "__main__":
    asyncio.run(main())
