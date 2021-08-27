# -*- coding: utf-8 -*-
"""DinnerlyMealScrape.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ialRqE1WRfkiNVjtcz9j3-10HY7DnJvD
"""


# The standard library modules
import os
import sys


# The BeautifulSoup module
from bs4 import BeautifulSoup

# The selenium module
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import requests
from unicodedata import numeric
import html2text
import pandas as pd
import json


def get_chroomme_options():
    sys.path.insert(0, "/usr/lib/chromium-browser/chromedriver")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return chrome_options


def getMeals(driver, url="https://dinnerly.com/menu"):
    success = False
    meals = {}
    while not success:
        driver.get(url)  # load the web page
        driver.implicitly_wait(5)  # seconds
        WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.ID, "menu-page__container"))
        )
        src = driver.page_source
        soup = BeautifulSoup(src, "html.parser")
        h = html2text.HTML2Text()
        if soup.find(string="menu-page__recipe"):
            success = True
        # print(soup)
        print("hi")
        for i in soup.find_all("div", attrs={"class": "menu-page__recipe"}):
            success = True
            a_link = i.find("a", href=True)
            name_and_image = h.handle(str(i.find("img")))
            a_link = str(a_link)
            print(a_link)
            path = a_link.split('href="')[1].split('"')[0]
            meal_name = a_link.split('alt="')[1].split('"')[0]
            link = f"https://dinnerly.com{path}"
            print(f"the meal is {meal_name} and link {link}")
            meals[meal_name] = link
    return meals


# convert weird fractions to the decimal
Fractions = {
    "¼": 0.25,
    "½": 0.5,
    "¾": 0.75,
    "⅕": 0.2,
    # add any other fractions here
}

units = ["oz", "lb", "count"]


def getIngredients(driver, url, meal_name):

    # driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options) # if you want to use chrome, replace Firefox() with Chrome()
    fullDownload = False
    while fullDownload == False:
        driver.get(url)  # load the web page
        WebDriverWait(
            driver, 50, poll_frequency=1000
        )  # .until(EC.visibility_of_element_located((By.CLASS_NAME, "dish-detail__ingredient nui__col-2")))
        src = driver.page_source
        soup = BeautifulSoup(src, "html.parser")
        h = html2text.HTML2Text()
        meal_ingred_data = {
            "quantity": [],
            "unit": [],
            "ingredient": [],
            "link": [],
            "meal_name": [],
        }

        for i in soup.find_all(
            "div", attrs={"class": "dish-detail__ingredient nui__col-2"}
        ):
            fullDownload = True
            full_ingredient = h.handle(str(i.find("p")))
            unit = None
            # print(full_ingredient)
            for a_unit in units:
                if a_unit in full_ingredient:
                    unit = a_unit

            if unit is None:
                unit = "count"
                if "pkt" in full_ingredient or "pkg" in full_ingredient:
                    parts = full_ingredient.split("pkt")
                    quantity = convertToDecimal(parts[0].strip())
                    ingredient = parts[1].strip()
                else:
                    vals = [int(s) for s in full_ingredient.split() if s.isdigit()]
                    if len(vals) == 0:
                        quantity = 1
                        ingredient = full_ingredient.strip()
                    else:
                        quantity = vals[0]
                        ingredient = full_ingredient.split(str(vals[0]))[1].strip()
            else:
                # edge case:
                # 2 (2 oz) pkts shredded cheddar-jack blen
                prefix = ""
                if "pkts" in full_ingredient:
                    parts = full_ingredient.split("pkts")
                    count = int(parts[0].split(" (")[0])
                    quantity = (
                        convertToDecimal(
                            parts[0].split("(")[1].split(f"{unit}")[0].strip()
                        )
                        * count
                    )
                    ingredient = parts[1].strip()
                elif "pkt" in full_ingredient:
                    if "(" in full_ingredient:

                        parts = full_ingredient.split("pkt")
                        count = int(parts[0].split(" (")[0])
                        quantity = (
                            convertToDecimal(
                                parts[0].split("(")[1].split(f"{unit}")[0].strip()
                            )
                            * count
                        )
                        ingredient = parts[1].strip()

                    else:
                        prefix = "pkt"
                        parts = full_ingredient.split(f"{unit} {prefix}")
                        quantity = convertToDecimal(parts[0].strip())
                        ingredient = parts[1].strip()
                elif "pkg" in full_ingredient:
                    if "(" in full_ingredient:
                        parts = full_ingredient.split("pkg")
                        count = int(parts[0].split(" (")[0])
                        quantity = (
                            convertToDecimal(
                                parts[0].split("(")[1].split(f"{unit}")[0].strip()
                            )
                            * count
                        )
                        ingredient = parts[1].strip()
                    else:
                        prefix = "pkg"
                        parts = full_ingredient.split(f"{unit} {prefix}")
                        quantity = convertToDecimal(parts[0].strip())
                        ingredient = parts[1].strip()
                else:
                    parts = full_ingredient.split(f"{unit} {prefix}")
                    quantity = convertToDecimal(parts[0].strip())
                    ingredient = parts[1].strip()

            meal_ingred_data["quantity"].append(quantity)
            meal_ingred_data["unit"].append(unit)
            meal_ingred_data["ingredient"].append(ingredient)
            meal_ingred_data["link"].append(url)
            meal_ingred_data["meal_name"].append(meal_name)

            print(f"quantity = {quantity} unit = {unit} c = {ingredient}")
    return meal_ingred_data


def convertToDecimal(i):

    if len(i) == 1 and i.isnumeric():
        v = numeric(i)
    elif i[-1].isdigit():
        # normal number, ending in [0-9]
        v = float(i)
    else:
        # Assume the last character is a vulgar fraction
        v = float(i[:-1]) + numeric(i[-1])
    return v


def minDis(s1, s2, n, m, dp):

    # If any string is empty,
    # return the remaining characters of other string
    if n == 0:
        return m
    if m == 0:
        return n

    # To check if the recursive tree
    # for given n & m has already been executed
    if dp[n][m] != -1:
        return dp[n][m]

    # If characters are equal, execute
    # recursive function for n-1, m-1
    if s1[n - 1] == s2[m - 1]:
        if dp[n - 1][m - 1] == -1:
            dp[n][m] = minDis(s1, s2, n - 1, m - 1, dp)
            return dp[n][m]
        else:
            dp[n][m] = dp[n - 1][m - 1]
            return dp[n][m]

    # If characters are nt equal, we need to
    # find the minimum cost out of all 3 operations.
    else:
        if dp[n - 1][m] != -1:
            m1 = dp[n - 1][m]
        else:
            m1 = minDis(s1, s2, n - 1, m, dp)

        if dp[n][m - 1] != -1:
            m2 = dp[n][m - 1]
        else:
            m2 = minDis(s1, s2, n, m - 1, dp)
        if dp[n - 1][m - 1] != -1:
            m3 = dp[n - 1][m - 1]
        else:
            m3 = minDis(s1, s2, n - 1, m - 1, dp)

        dp[n][m] = 1 + min(m1, min(m2, m3))
        return dp[n][m]


def getKrogerToken():
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"

    test_api_url = "https://api.kroger.com/v1/"

    # client (application) credentials on apim.byu.edu
    client_id = "changeme"
    client_secret = "changeme"
    scope = "product.compact"

    # step A, B - single call with client credentials as the basic auth header - will return access_token
    data = {"grant_type": "client_credentials", "scope": scope}

    access_token_response = requests.post(
        token_url,
        data=data,
        verify=False,
        allow_redirects=False,
        auth=(client_id, client_secret),
    )

    # print(access_token_response.headers)
    # print(access_token_response.text)

    tokens = json.loads(access_token_response.text)

    # print("access token: " + tokens['access_token'])
    return tokens["access_token"]


def getLocationID(zip, token):
    url = f"https://api.kroger.com/v1/locations?filter.zipCode.near={zip}&filter.radiusInMiles=10&filter.limit=1&filter.chain=Kroger"

    api_call_headers = {"Authorization": "Bearer " + token}
    api_call_response = requests.get(url, headers=api_call_headers, verify=False)
    location_id = json.loads(api_call_response.text)["data"][0]["locationId"]
    # print(api_call_response.text)
    # print(location_id)
    return location_id


def getKrogerProductInfo(item, location_id, token):
    product_url = f"https://api.kroger.com/v1/products?filter.term={item}&filter.locationId={location_id}"

    api_call_headers = {"Authorization": "Bearer " + token}
    api_call_response = requests.get(
        product_url, headers=api_call_headers, verify=False
    )

    # print(json.loads(api_call_response.text)['data'][0].keys())
    jsondata = json.loads(api_call_response.text)["data"]
    results = []
    minDist = 100
    for el in jsondata:
        product_info = el["description"]
        regular_product_price = el["items"][0]["price"]["regular"]
        sale_price = el["items"][0]["price"]["promo"]
        size = el["items"][0]["size"]
        quantity = 0
        unit = "count"

        sizeSplit = size.split(" ")
        if len(sizeSplit) > 2:
            # don't know how to parse weird things...
            continue

        if len(sizeSplit) > 1:
            unit = sizeSplit[1]
            quantity = float(sizeSplit[0])
            if unit == "lb":
                quantity = 16.0 * quantity
                unit = "oz"
        else:
            unit = float(sizeSplit[0])

        if sale_price == 0:
            tempUnitCost = regular_product_price / quantity
        else:
            tempUnitCost = sale_price / quantity

        soldBy = el["items"][0]["soldBy"]
        upc = el["upc"]
        n = len(item)
        m = len(product_info)
        dp = [[-1 for i in range(m + 1)] for j in range(n + 1)]

        ed = minDis(item, product_info, len(item), len(product_info), dp)
        prodData = {
            "product_info": product_info,
            "product_price": regular_product_price,
            "unit_price": tempUnitCost,
            "sale_price": sale_price,
            "unit": unit,
            "quantity": quantity,
            "size": size,
            "soldBy": soldBy,
            "upc": upc,
            "ed": ed,
        }

        results.append(prodData)

    resultsdf = pd.concat([pd.DataFrame(d, index=[0]) for d in results], axis=0)
    minEdDistDF = (
        resultsdf[resultsdf["ed"] <= resultsdf["ed"].min() + resultsdf["ed"].std()]
        .copy()
        .reset_index(drop=True)
    )
    bestUnitPrice = (
        minEdDistDF[minEdDistDF["unit_price"] == minEdDistDF["unit_price"].min()]
        .copy()
        .reset_index(drop=True)
    )
    return bestUnitPrice


def getKrogerProduct(item, zip=23434):
    token = getKrogerToken()
    location_id = getLocationID(zip, token)
    return getKrogerProductInfo(item, location_id, token)


"""https://dvenkatsagar.github.io/tutorials/python/2015/10/26/ddlv/
https://www.crummy.com/software/BeautifulSoup/bs4/doc/
https://stackoverflow.com/questions/51046454/how-can-we-use-selenium-webdriver-in-colab-research-google-com
https://github.com/Alir3z4/html2text

"""


def getReceipeInfo():
    chrome_options = get_chroomme_options()
    driver = webdriver.Chrome("chromedriver", chrome_options=chrome_options)
    meals = getMeals(driver)

    allData = []
    for k, v in meals.items():
        if "Add an Extra" not in k:
            print(f"{k} {v}")
            ingredients = getIngredients(driver, v, k)
            allData.append(ingredients)

    recipeInfo = pd.concat([pd.DataFrame(d) for d in allData])


# going to make the user tag the type of receipe...
# types = ['beef', 'chicken', 'burger', 'pork']
# recipeInfo['meal_name'].unique()
