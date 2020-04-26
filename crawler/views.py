from django.shortcuts import render
from django.http import JsonResponse
from utils import utils
from .models import Crawled

# Create your views here.
def index(request):
	return render(request, 'crawler.html')

def crawler(request):

	siteinfos = request.GET.getlist('siteinfos[]')
	for siteinfo in siteinfos:
		info = siteinfo.split(',')
		# 사이트, 아이디, 패스워드, 키워드
		site = info[0]
		id = info[1]
		pwd = info[2]
		keyword = info[3]
		result = utils.crawling(site, id, pwd, keyword)

		for key in result.keys():
			crawled_data = result[key]
			crawled = Crawled(keyword=keyword, site=site, used_id=id
			                  , product_name=crawled_data[0]
			                  , product_price=crawled_data[1]
			                  , company=crawled_data[2]
			                  , price=crawled_data[3]
			                  , discount_price=crawled_data[4])
			crawled.save()

	return JsonResponse({"success": True})
