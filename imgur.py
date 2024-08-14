import matplotlib
matplotlib.use('Agg')
import datetime
from imgurpython import ImgurClient
client_id = '4670b4b0bf170b4'
client_secret = '09a0efe9887546ed478ec7b47bc520df454ba78c'
album_id = 'JZT1G9u'
access_token = '41f671cf030cba2752460825433488e08d9a2e9f'
refresh_token = '0346f2d72d4c80bdd02f4c52149669ce2c412213'


def showImgur(fileName):
    client = ImgurClient(client_id,client_secret,access_token,refresh_token)

    config = {
        'album':album_id,
        'name':fileName,
        'title':fileName,
        'description':str(datetime.date.today())
    }

    try:
        print('正在載入你的圖片')
        imgurl = client.upload_from_path(fileName + '.png',config=config,anon=False)['link']
        print('載入完成')

    except:
        imgurl = 'https://picsum.photos/seed/picsum/200/300'
        print('[log:ERROR]Unable upload!!')


    return imgurl