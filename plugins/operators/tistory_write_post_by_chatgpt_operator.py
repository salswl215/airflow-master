from config.chatgpt import get_chatgpt_response
from config.pykrx_api import get_prompt_for_chatgpt
import pendulum
from random import randrange

from airflow.models.baseoperator import BaseOperator
from airflow.models import Variable


class GetInfoByChatgptOperator(BaseOperator):
    def __init__(self, post_cnt_per_market: int, **kwargs):
        super().__init__(**kwargs)
        self.post_cnt_per_market = post_cnt_per_market

    def execute(self, context):
        chatgpt_api_key = Variable.get('chatgpt_api_key')

        now = pendulum.now('Asia/Seoul')
        now_yyyymmmdd = now.strftime('%Y%m%d')
        yyyy = now.year
        mm = now.month
        dd = now.day
        hh = now.hour
        kospi_ticker_name_lst, kospi_fluctuation_rate_lst, prompt_of_kospi_top_n_lst = get_prompt_for_chatgpt(
            now_yyyymmmdd, market='KOSPI', cnt=self.post_cnt_per_market)
        kosdaq_ticker_name_lst, kosdaq_fluctuation_rate_lst, prompt_of_kosdaq_top_n_lst = get_prompt_for_chatgpt(
            now_yyyymmmdd, market='KOSDAQ', cnt=self.post_cnt_per_market)

        tot_ticker_name_lst = kospi_ticker_name_lst + kosdaq_ticker_name_lst
        tot_fluctuation_rate_lst = kospi_fluctuation_rate_lst + kosdaq_fluctuation_rate_lst
        tot_prompt = prompt_of_kospi_top_n_lst + prompt_of_kosdaq_top_n_lst

        market = 'KOSPI'
        for idx, prompt in enumerate(tot_prompt):
            temperature = randrange(10, 100) / 100  # 0.1 ~ 1 사이
            ticker_name = tot_ticker_name_lst[idx]
            print(f'ticker: {ticker_name}, temperature:{temperature}')  # temperature 확인용 로깅

            fluctuation_rate = tot_fluctuation_rate_lst[idx]
            fluctuation_rate = round(fluctuation_rate, 1)
            chatgpt_resp = get_chatgpt_response(api_key=chatgpt_api_key,
                                                prompt=prompt,
                                                temperature=temperature)
            chatgpt_resp = chatgpt_resp.replace('\n', '<br/>')

            if idx >= self.post_cnt_per_market:
                market = 'KOSDAQ'

            print(chatgpt_resp)