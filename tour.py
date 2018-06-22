# 상품정보를 담는 클래스

class TourInfo:
    # 멤버변수
    title = ''
    price = ''
    area = ''
    link = ''
    img = ''
    contents = ''
    # 생성
    def __init__(self, title, price, area, link, img, contents=None):
        self.title = title
        self.price = price
        self.area = area
        self.link = link
        self.img = img
        self.contents = contents
