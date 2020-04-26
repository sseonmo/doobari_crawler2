from django.contrib import admin
from .models import Crawled
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

# Register your models here.

class CrawledAdmin(admin.ModelAdmin):
	list_display = ('keyword', 'site', 'product_name', 'product_price', 'company', 'price', 'discount_price', 'created_at')
	list_filter = (('created_at', DateTimeRangeFilter), 'site', 'keyword', 'company',)
	search_fields = ('product_name',)
	ordering = ('-created_at',)


admin.site.register(Crawled, CrawledAdmin)



