#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\vgs\common\utils.py
import collections
import evetypes
import json
Product = collections.namedtuple('Product', ['id', 'name', 'href'])
ProductQuantity = collections.namedtuple('ProductQuantity', ['typeId',
 'quantity',
 'name',
 'imageUrl'])
OfferPricing = collections.namedtuple('OfferPricing', ['currency', 'price', 'basePrice'])
Offer = collections.namedtuple('Offer', ['id',
 'name',
 'description',
 'href',
 'offerPricings',
 'imageUrl',
 'productQuantities',
 'categories',
 'label',
 'goodsID',
 'canPurchase',
 'singlePurchase'])
Category = collections.namedtuple('Category', ['id',
 'name',
 'href',
 'parentId',
 'subcategories',
 'tagIds',
 'categoryTags'])
Label = collections.namedtuple('Label', ['name', 'description', 'url'])

def create_offer_from_json(offer_json):
    third_party_info = offer_json.get('thirdpartyinfo', None)
    if third_party_info is not None:
        goods_id = third_party_info.get('goodsid', None)
    else:
        goods_id = None
    offer_pricings = [ OfferPricing(pricing['currency'], pricing['price'], pricing['basePrice']) for pricing in offer_json['offerPricings'] ]
    product_quantities = {}
    for product in offer_json['products']:
        try:
            name = product['productName']
            image_url = product['imageUrl']
        except KeyError:
            name = None
            image_url = None

        if product['typeId'] > 0:
            name = evetypes.GetName(product['typeId'])
        if name:
            product_quantities[product['id']] = ProductQuantity(product['typeId'], product['quantity'], name, image_url)

    return Offer(offer_json['id'], offer_json['name'], offer_json['description'], offer_json['href'], offer_pricings, offer_json['imageUrl'], product_quantities, {category['id'] for category in offer_json['categories']}, create_label_from_json(offer_json['label']) if offer_json['label'] is not None else None, goods_id, offer_json['canPurchase'], offer_json['singlePurchase'])


def create_label_from_json(label_json):
    return Label(label_json['name'], label_json['description'], label_json['url'])


def create_category_from_json(category_json):
    return Category(category_json['id'], category_json['name'], category_json['href'], category_json['parent']['id'] if category_json['parent'] is not None else None, set(), set(), category_json.get('tags', set()))


def create_product_from_json(product_json):
    return Product(product_json['id'], product_json['name'], product_json['href'])
