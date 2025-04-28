from airflow.hooks.base import BaseHook
import psycopg2
import pandas as pd

class CustomPostgresHook(BaseHook):

    def __init__(self, postgres_conn_id, **kwargs):
        self.postgres_conn_id = postgres_conn_id

    # get_conn 메소드 정의 : postgres 연결 정보 받아와 postgres 연결 세션 생성
    def get_conn(self):
        # get_connection 메소드의 경우 airflow connections에 저장한 정보 불러오는 메소드
        # get_connection은 클래스 메소드로 객체 생성하지 않고 바로 쓸 수 있음
        airflow_conn = BaseHook.get_connection(self.postgres_conn_id)
        self.host = airflow_conn.host
        self.user = airflow_conn.login
        self.password = airflow_conn.password
        self.dbname = airflow_conn.schema
        self.port = airflow_conn.port

        self.postgres_conn = psycopg2.connect(host = self.host,
                                              user = self.user,
                                              password = self.password,
                                              dbname = self.dbname,
                                              port = self.port)
        return self.postgres_conn

    def bulk_load(self, table_name, file_name, delimeter: str, is_header: bool, is_replace: bool):
        from sqlalchemy import create_engine

        self.log.info('적재 대상파일' + file_name)
        self.log.info('테이블 :' + table_name)
        self.get_conn()
        header = 0 if is_header else None
        if_exists = 'replace' if is_replace else 'append'
        file_df = pd.read_csv(file_name, header = header, delimiter=delimeter)

        # 줄넘김 및 ^M 제거
        for col in file_df.columns:
            try:
                # string 문자열이 아닌 경우 continue
                file_df[col] = file_df[col].str.astype('\r\n', '')
                self.log.info(f'{table_name}.{col}: 개행문자 제거')
            except:
                continue

        self.log.info('적재 건수' + str(len(file_df)))
        uri = f'postgresql://{self.user}:{self.password}@{self.host}/{self.dbname}'
        engine = create_engine(uri)
        file_df.to_sql(name = table_name,
                       con=engine,
                       schema='public',
                       if_exists=if_exists,
                       index=False)