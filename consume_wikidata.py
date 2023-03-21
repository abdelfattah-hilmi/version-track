import requests
import json
import re
from bs4 import BeautifulSoup

def get_PackageName_version(PackageName):
    url = "https://www.wikidata.org/w/index.php?go=Go&search={PackageName}"

    # Send a GET request to the URL and store the response
    response = requests.get(url)

    # Use Beautiful Soup to parse the HTML content of the response
    soup = BeautifulSoup(response.content, 'html.parser')

    element = soup.find("span", class_="wb-itemlink-id")
    text = element.text
    pattern = r"\w+"
    match = re.search(pattern, text)
    if match:
        alphanumeric_string = match.group()
    else:
        alphanumeric_string = None

    response = requests.get("https://www.wikidata.org/w/rest.php/wikibase/v0/entities/items/" + alphanumeric_string + "/statements" )
    data = json.loads(response.text)
    filtered_array = list(filter(lambda obj: obj['rank'] == 'preferred',data['P348']))

    def extractAndCast(string):
        pattern = r"\d{1,2}\.\d{1,2}\.\d{1,2}"
        match = re.search(pattern, string)
        num = int(match.group(0).replace(".", ""))
        return num

    max_version = 0
    targetObject = {}
    references = []
    for object in filtered_array:
        if extractAndCast(object["value"]["content"]) > max_version:
            targetObject = object
            max_version = extractAndCast(object["value"]["content"])

    for reference in targetObject["references"]:
        for part in reference["parts"]:
            if (part.get("property") and part["property"].get("data-type") == "url") or ( part.get("id") and part.get("id") == "P854"):
                references.append(part["value"]["content"])

    return {"Version": targetObject["value"]["content"], "Reference": references}