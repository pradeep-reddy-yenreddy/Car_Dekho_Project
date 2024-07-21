import pandas as pd
from bs4 import BeautifulSoup
import requests


class Webscrapping:
    def __init__(self):
        self.main_url = "https://www.cardekho.com/filter/new-cars"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.base = "https://www.cardekho.com"

    def get_response_from_url(self):
        response = requests.get(self.main_url, self.headers)
        return BeautifulSoup(response.content, "html.parser")

    def table_page_url(self):
        varient_details = []
        soup = self.get_response_from_url(self.main_url)
        table_tag = soup.find("table", class_="allvariant contentHold")
        if table_tag:
            # Finding all <td> tags within the table
            td_tags = table_tag.find_all("td")

            for td in td_tags:
                variant_link = td.find("a")
                if variant_link:
                    variant_url = variant_link["href"]
                    self.main_url = self.base + variant_url
                    varient_details.append(self.extract_final_details())
        return varient_details

    def extract_final_details(self):
        soup = self.get_response_from_url(self.main_url)
        Key_Spec_list = []
        key_specs = soup.find("div", attrs={"data-track-section": "Key Specifications"})
        if key_specs:
            Key_sp = key_specs.find_all("tr")
            for tr in Key_sp:
                Key_Spec_list.append(tr.get_text(strip=True))

        Top_Features_list = []
        top_features = soup.find("div", attrs={"data-track-section": "Top Features"})
        # top_features_div = [row.get_text(strip=True) for row in top_features.find_all('ul')]
        if top_features:
            Top = top_features.find_all("ul")
            for t in Top:
                Top_features = t.find_all("li")
                for li in Top_features:
                    if li.find("i", class_="icon-check"):
                        Top_Features_list.append(li.get_text(strip=True))

        Price_Detail_list = []
        Price_tag = soup.find("section", id="OnRoadPrice")
        if Price_tag:
            All_combined_Prices = Price_tag.find_all("tr")
            for prices in All_combined_Prices:
                for p in prices.find_all("span", class_="othersinfo"):
                    p.decompose()
                Price_Detail_list.append(prices.get_text(strip=True))

        Spec_Feature_list = []
        Spec_features = soup.find("div", class_="specsTblNew")
        if Spec_features:
            # all_specs=[ r.get_text() for r in Spec_features.find_all('tr')]
            all_specs = Spec_features.find_all("tr")
            for rows in all_specs:
                row = rows.find_all("td")
                for r in row:
                    for x in r.find_all("div", class_="tootTipCtr"):
                        x.decompose()
                    for y in r.find_all("span", class_="link hover wrongprice"):
                        y.decompose()
                    for z in r.find_all("i", class_="icon-deletearrow"):
                        z.append("No")
                    for k in r.find_all("i", class_="icon-check"):
                        k.append("Yes")
                    Spec_Feature_list.append(r.get_text(strip=True))

        fetching_name = soup.find_all(
            "div",
            class_="gsc_col-xs-12 gsc_col-sm-12 gsc_col-md-7 gsc_col-lg-7 overviewdetail",
        )
        for model in fetching_name:
            Car_name = model.find("h1", class_="displayInlineBlock")
            Car_name

        def listToString(s):
            stg = ""
            for x in s:
                stg = stg + x + "	"
            return stg.rstrip()

        car_details = {}
        car_details["name"] = Car_name.text
        car_details["price_details"] = listToString(Price_Detail_list)
        car_details["top_features"] = listToString(Top_Features_list)
        car_details["key_specs"] = listToString(Key_Spec_list)
        car_details["all_features_and_specs"] = listToString(Spec_Feature_list)

        # car_details_df=pd.DataFrame([car_details])

        return car_details


obj = Webscrapping()
soup = obj.get_response_from_url()

total_models = soup.find_all(
    "div", class_="gsc_col-md-12 gsc_col-sm-12 gsc_col-xs-12 append_list"
)
varient_details = []
for model in total_models:
    h3_tag = model.find("h3")
    if h3_tag:
        a_tag = h3_tag.find("a", href=True)
        if a_tag:
            page2_url = a_tag["href"]
            obj.url = obj.base + page2_url
            varient_details.extend(obj.table_page_url())
car_data = pd.DataFrame(varient_details)
car_data.to_csv("Alldata.csv")
