import os
################ AUTHENTICATION VARIABLES ####################
SHOP_ID = os.getenv("SHOP_ID")
PARTNER_ID = os.getenv("PARTNER_ID")
SECRET_KEY = os.getenv("SECRET_KEY")


######################### ROUTES #############################
IMAGE_PC_ONE_ROUTE = r'\\192.168.100.48\shopee_img\\'
IMAGE_PC_TWO_ROUTE = r'\\192.168.100.58\shopee_img\\'
USED_BOOK_TAG_IMG_ROUTE = r'D:\shopee\images\\'
LOG_PATH = r'D:\shopee\log'
SHOPEE_IMAGE_SERVER_URL = 'https://s-cf-tw.shopeesz.com'
TAAZE_SHOPEE_IMAGE_URL = 'https://media.taaze.tw/ShopeeImg/{}.png'
TAAZE_IMAGE_URL = 'https://media.taaze.tw/showThumbnailByPk.html?sc={}&height={}&width={}'


######################## VARIABLES ###########################
DEFAULT_BRAND = '自有品牌'

NEW_BOOK_ID = '111'
USED_BOOK_ID = '113'
MAGZINE_CHINESE = '211'
MAGZINE_US = '231'
MAGZINE_MOOK = '241'
USED_MAGZINE_MOOK = '243'
STATIONERY = '611'
BAZAAR = '621'
DVD = '321'
MAGZINE_JAPAN = '271'
USED_MAGZINE_JAPAN = '273'
USED_BOOK_US = '133'
MAGZINE_KOREA = '221'
NEW_BOOK_SIMPLE = '121'
USED_BOOK_SIMPLE = '123'

IMAGE_TARGET_HEIGHT = 800
IMAGE_TARGET_WIDTH = 800
IMAGE_MIN_SIZE = 200
MAX_IMAGES_PER_ITEM = 10


######################## ERROR MSG ###########################
IMG_TOO_SMALL_ERROR = '圖片太小'
DOWNLOAD_FAIL_ERROR = '下載失敗'
NO_IMAGES_ERROR = '沒有圖片'


################## API RRESPONSE PARAMS ######################
SHOPEE_ADD_ITEM_SUCCESS = 'Add item success'
SHOPEE_DOWNLOAD_ERROR = 'error_param'