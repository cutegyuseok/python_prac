from flask import Flask, render_template, request, jsonify
import requests
import xml.etree.ElementTree as ET
from pymongo.mongo_client import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb+srv://<아이디>:<비번>@cluster0.yf4pqg5.mongodb.net/?retryWrites=true&w=majority')
db = client.oss


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        keyword = request.form['keyword']
        recipe_names = get_recipe_names(keyword)
        return jsonify(recipe_names)
    return render_template('main.html')


def get_recipe_names(keyword):
    url = f"http://211.237.50.150:7080/openapi/<key>/xml/Grid_20150827000000000226_1/1/500"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    recipe_names = []
    for item in root.iter('row'):
        name = item.find('RECIPE_NM_KO').text
        if keyword.lower() in name.lower():
            recipe_names.append(name)
    return recipe_names


@app.route('/search/<keyword>', methods=['GET'])
def search(keyword):
    instance = get_recipe_names(keyword)
    db.recipes.insert_one(instance)
    return instance


def get_recipe(keyword):
    url1 = f"http://211.237.50.150:7080/openapi/<key>/xml/Grid_20150827000000000226_1/1/1?RECIPE_NM_KO={keyword}"
    res = requests.get(url1)
    root = ET.fromstring(res.content)

    for item in root.iter('row'):
        recipe_id = item.find('RECIPE_ID').text
        url2 = f"재료API?RECIPE_ID={recipe_id}"
        res2 = requests.get(url2)
        root2 = ET.fromstring(res2.content)

        ingredient_list = []
        for item2 in root2.iter('row'):
            ingredient = {
                'ingredient_name': item2.find('IRDNT_NM').text,
                'ingredient_capacity': item2.find('IRDNT_CPCTY').text,
                'ingredient_type': item2.find('IRDNT_TY_NM').text,
            }
            ingredient_list.append(ingredient)

        instance = {
            'recipe_id': item.find('RECIPE_ID').text,
            'RECIPE_NM_KO': item.find('RECIPE_NM_KO').text,
            'SUMRY': item.find('SUMRY').text,
            'NATION_NM': item.find('NATION_NM').text,
            'QNT': item.find('NATION_NM').text,
            'ingredients': ingredient_list
        }
        return instance


if __name__ == '__main__':
    app.run(debug=True)
