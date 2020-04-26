from django.db import models

# Create your models here.

class Crawled(models.Model):
	# 제품명, 제품가격 / product_name, product_price
	# 공급사 가격 세일가 재고
	# 업체명 일반가 할인가 재고
	keyword = models.CharField(max_length=100, verbose_name='검색키워드')
	site = models.CharField(max_length=100, verbose_name='사이트')
	used_id = models.CharField(max_length=100, verbose_name='아이디')
	product_name = models.CharField(max_length=100, verbose_name='제품명')
	product_price = models.IntegerField(verbose_name='제품가격')
	company = models.CharField(max_length=100, verbose_name='공급업체')
	price = models.IntegerField(verbose_name='공급_일반가')
	discount_price = models.IntegerField(verbose_name='공급_할인가')
	created_at = models.DateTimeField(verbose_name='등록시간', auto_now_add=True)
	modified_at = models.DateTimeField(verbose_name='수정시간', auto_now=True)

	def __str__(self):
		return "{} / 일반가 : {} / 할인가 : {}".format(self.company, str(self.price), str(self.discount_price))

	class Meta:
		db_table = "crawled_data"
		verbose_name = '업체가격정보'
		verbose_name_plural = '업체가격정보게시판'