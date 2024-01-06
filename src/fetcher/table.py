from dataclasses import dataclass
import logging
import re
from typing import Annotated, Any
import requests
from annotated_types import Ge, MinLen
from bs4 import BeautifulSoup, ResultSet
from pandas import ExcelWriter, DataFrame

from src.util import JsonUtil
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class TableIDName:
    table_id: str = "general"
    table_elem_index: int = 0
    head_id: str = "general"
    body_id: str = "general"
    row_id: str = "general"
    col_id: str = "general"

    @classmethod
    def initialize(cls, str_id: Annotated[str, MinLen(2)], index: int):
        return TableIDName(
            table_id=str_id, table_elem_index=index, head_id=str_id, body_id=str_id,
            row_id=str_id, col_id=str_id)


class DataFetch:

    def __init__(self):
        self.parse_config = JsonUtil.read(
            "parse.json", file_in_curr_dir=True, cur_file_path=__file__)

    def getfindattr(self, bsoup: BeautifulSoup, type_tag: str, case_tag: str,
                    limit: Annotated[int, Ge(1)] = 1) -> (bool, ResultSet):

        def getidval(_config: dict, key_id: str) -> Any:
            val = _config.get(key_id, None)
            if isinstance(val, str) and val.startswith("regex_"):
                _val = val.split("_")[1]
                val = re.compile(_val)
            return val

        if case_tag == "":
            return False, set()

        try:
            type_config = self.parse_config[type_tag][case_tag]
            assert isinstance(type_config, dict)
            assert any(key in type_config for key in ["tag", "attr", "class"])
        except AttributeError as a_err:
            logger.error("Config key are not found %s", a_err)
            return False, None

        tag_val = getidval(type_config, "tag")
        attr_val = getidval(type_config, "attr")
        class_val = getidval(type_config, "class")

        # Find the table on the webpage based on the provided taginfo
        if tag_val and attr_val:
            if class_val:
                res_set = bsoup.find_all(
                    name=tag_val, attrs=attr_val, class_=class_val, limit=limit)
            else:
                res_set = bsoup.find_all(name=tag_val, attrs=attr_val, limit=limit)
        elif tag_val:  # attr_val is None
            if class_val:
                res_set = bsoup.find_all(name=tag_val, class_=class_val, limit=limit)
            else:
                res_set = bsoup.find_all(name=tag_val, limit=limit)
        elif attr_val:  # tag_val is None
            if class_val:
                res_set = bsoup.find_all(attrs=attr_val, _class=class_val, limit=limit)
            else:
                res_set = bsoup.find_all(attrs=attr_val, limit=limit)
        else:  # class_val is None
            res_set = bsoup.find_all(class_=class_val, limit=limit)

        return True, res_set

    def extract_table_from_url(
            self, url: str, tab_meta_id: TableIDName) -> DataFrame:
        # Send an HTTP GET request to the URL
        response = requests.get(url, timeout=10)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            logger.warning("The url is incorrect  %s", url)
            return None   # Return None if the request to retrieve the webpage fails

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        res_t, tables = self.getfindattr(
            soup, "table", tab_meta_id.table_id, tab_meta_id.table_elem_index+2)
        if not res_t:
            logger.warning("The table data is incorrect")

        if not tables or len(tables) == 0:
            logger.warning("The url %s don't have table", url)
            return None   # Return None if the table is not found on the webpage

        if len(tables) < tab_meta_id.table_elem_index:
            logger.warning("The url %s don't have required table", url)
            return None   # Return None if the table is not found on the webpage

        table = tables[tab_meta_id.table_elem_index]
        header_row = []
        res_th, theader = self.getfindattr(table, "header", tab_meta_id.head_id, 2)
        if not res_t:
            logger.warning("The header is missing")
        else:
            _res_thc, cells = self.getfindattr(theader[0], "column", tab_meta_id.col_id, 500)
            # Extract text from each cell and store in a row list
            header_row = [cell.get_text(strip=True) for cell in cells]

        res_th, tbody = self.getfindattr(table, "body", tab_meta_id.body_id, 2)
        if not res_t:
            logger.warning("The tbody is missing")
            _tbody = table
        else:
            _tbody = tbody[0]

        extracted_table = []
        # Extract data from the table
        _res_row, table_rows = self.getfindattr(_tbody, "row", tab_meta_id.row_id, 500)

        for row in table_rows:
            # Get all table cells in each row
            _res_tbc, cells = self.getfindattr(row, "column", tab_meta_id.col_id, 500)

            # Extract text from each cell and store in a row list
            row_data = [cell.get_text(strip=True) for cell in cells]
            extracted_table.append(row_data)

        if header_row:
            pdata = DataFrame(data=extracted_table, columns=header_row)
        else:
            pdata = DataFrame(data=extracted_table)

        return pdata   # Return the table as DataFrame



def collect_inv_data():
    _id_name_inv = TableIDName()
    _id_name_inv.table_id = "investing"
    data_fetch = DataFetch()

    urls = ["https://in.investing.com/indices/s-p-cnx-nifty-components",
            "https://in.investing.com/indices/s-p-cnx-nifty-components-fundamental"]
    with ExcelWriter("./investing_components.xlsx", mode="w") as writer:
        for url in urls:
            dframe = DataFetch().extract_table_from_url(url, tab_meta_id=_id_name_inv)
            print(dframe)
            urlparts = urlparse(url)
            dframe.to_excel(writer, sheet_name=urlparts.path.rsplit("/", 1)[-1])


def collect_equitypandit_data():
    _id_name_inv = TableIDName()
    data_fetch = DataFetch()

    url = "https://www.equitypandit.com/list/nifty-50-companies"
    with ExcelWriter("./investing_components1.xlsx", mode="w") as writer:
        dframe = DataFetch().extract_table_from_url(url, tab_meta_id=_id_name_inv)
        print(dframe)
        urlparts = urlparse(url)
        dframe.to_excel(writer, sheet_name=urlparts.path.rsplit("/", 1)[-1])



if __name__ == "__main__":
    # collect_inv_data()
    collect_equitypandit_data()

    _id_name_zer = TableIDName.initialize("zerodha", 0)
    _id_name_zer.head_id, _id_name_zer.body_id = "", ""
    # URL = 'https://stocks.zerodha.com/indices/nifty-50-index-.NSEI/constituents?type=marketcap'
    #
    # EXTRACTED_TABLE = DataFetch().extract_table_from_url(
    #     URL, table_id="zerodha", row_id="zerodha", column_id="zerodha", table_elem_index=0)

    # if EXTRACTED_TABLE is not None:
    #     for row in EXTRACTED_TABLE:
    #         print(row)
    # else:
    #     print('Table not found or failed to retrieve the webpage.')
    #
    #     dfs = pd.read_html(URL)
    #     df = dfs[0]
    #     print(df)

        
