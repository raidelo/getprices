import requests, bs4
import datetime, time

class Scrapper:
    def __init__(self):
        self.__url_standard = 'https://eltoque.com/tasas-de-cambio-de-moneda-en-cuba-hoy'
        self.__url_cripto = 'https://api.cambiocuba.money/api/v1/x-rates-by-date-range-history'
        self.usd_compra, self.usd_venta = None, None
        self.usd_min, self.usd_max = None, None
        self.eur_compra, self.eur_venta = None, None
        self.eur_min, self.eur_max = None, None
        self.mlc_compra, self.mlc_venta = None, None
        self.mlc_min, self.mlc_max = None, None
        self.usdt_compra, self.usdt_venta = None, None

        self.__soup = None

        self.debug_info = 0

    def gtn(self, string_):
        return print('%s %s'%(datetime.datetime.now().time(), string_)) if self.debug_info else None

    def scrap(self):
        self.gtn('Initiating Scraping')
        start = time.time()
        self.gtn('Initiating Petition To ElToque\'s Page')
        page_standard = requests.get(self.__url_standard)
        self.gtn('Petition To ElToque\'s Page Elapsed Time: %s ... Real Duration: %f'%(page_standard.elapsed, time.time()-start))
        self.gtn('Started Fiat Prices Fetching')
        self.__soup = bs4.BeautifulSoup(page_standard.content, 'html.parser')
        self.gtn('Parsing USD Compra/Venta')
        self.usd_compra, self.usd_venta = self.__get_price('usd', 'compra'), self.__get_price('usd', 'venta')
        self.gtn('Parsing USD Max/Min')
        self.usd_min, self.usd_max = self.__get_price('usd', 'min'), self.__get_price('usd', 'max')
        self.gtn('Parsing EUR Compra/Venta')
        self.eur_compra, self.eur_venta = self.__get_price('eur', 'compra'), self.__get_price('eur', 'venta')
        self.gtn('Parsing EUR Max/Min')
        self.eur_min, self.eur_max = self.__get_price('eur', 'min'), self.__get_price('eur', 'max')
        self.gtn('Parsing MLC Compra/Venta')
        self.mlc_compra, self.mlc_venta = self.__get_price('mlc', 'compra'), self.__get_price('mlc', 'venta')
        self.gtn('Parsing MLC Max/Min')
        self.mlc_min, self.mlc_max = self.__get_price('mlc', 'min'), self.__get_price('mlc', 'max')
        self.gtn('Finshed Fiat Prices Fetching')
        self.gtn('Started Cripto Prices Fetching')
        self.usdt_compra = self.__get_price('usdt', 'compra')
        self.usdt_venta = self.__get_price('usdt', 'venta')
        self.gtn('Finished Cripto Prices Fetching')
        self.gtn('Finished Parsing')
        self.gtn('Total Elapsed Time: %f'%(time.time()-start))
        return self

    def __get_price(self, coin:str, mode:str) -> float:
        if not self.__soup:
            return 0.0
        coin, mode = coin.lower(), mode.lower()
        coins_standard = {'eur':0, 'usd':1, 'mlc':2}
        coins_cripto = {'usdt':'USDT_TRC20', 'btc':'BTC', 'bnb':'BNB', 'trx':'TRX'}
        #period = ['7D', '30D', '92D', '182D', '365D']
        #trmi = ['true', 'false']
        if coin in coins_standard.keys():
            modes_standard = {'venta':0, 'compra':1, 'min':0, 'max':1}
            if mode in ['compra', 'venta']:
                id_value = 'informal-compra-venta'
            elif mode in ['min', 'max']:
                id_value = 'informal-min-max'
            price = self.__soup.find('div', {'id':id_value}).find('tbody').find_all('td', {'class':'price-cell'})[coins_standard[coin]].find_all('span', {'class':'price-text'})[modes_standard[mode]].text
            return price
        elif coin in coins_cripto.keys():
            modes_cripto = {'compra':'Compra', 'venta':'Venta'}
            params = {
            'cur':coins_cripto[coin],
            'offer':modes_cripto[mode],
            'period':'7D', 'trmi':'true'}
            start = time.time()
            self.gtn('Parsing USDT %s'%modes_cripto[mode])
            response = requests.get(self.__url_cripto, params=params)
            self.gtn('Petition To Cripto Prices API Elapsed Time: %s ... Real Duration: %f'%(response.elapsed, time.time()-start))
            content = response.json()
            if len(content) == 0:
                return 0.0
            return content[-1]['median']

if __name__ == '__main__':
    sc = Scrapper().scrap()

    standard = f'''
1 EUR -> COMPRA {sc.eur_compra}  |  VENTA {sc.eur_venta}  |  MINIMOS({sc.eur_min})  MÁXIMOS({sc.eur_max})
1 USD -> COMPRA {sc.usd_compra}  |  VENTA {sc.usd_venta}  |  MINIMOS({sc.usd_min})  MÁXIMOS({sc.usd_max})
1 MLC -> COMPRA {sc.mlc_compra}  |  VENTA {sc.mlc_venta}  |  MINIMOS({sc.mlc_min})  MÁXIMOS({sc.mlc_max})
'''
    cripto = '1 USDT -> COMPRA %.2f CUP  |  VENTA %.2f CUP\n'

    usdt_compra, usdt_venta = sc.usdt_compra, sc.usdt_venta

    print(standard)
    print(cripto %(usdt_compra, usdt_venta))