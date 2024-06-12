# myapp/models.py
from django.db import models

class HomeShopping(models.Model):
    home_shopping_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    home_shopping_image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'HomeShopping'


class Product(models.Model):
    #product_id = models.AutoField(primary_key=True)   // data type 변경되어서 수정함
    product_id = models.CharField(primary_key=True, max_length=255)
    home_shopping = models.ForeignKey(HomeShopping, on_delete=models.CASCADE)
    product_url = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    price = models.IntegerField()
    product_image_url = models.CharField(max_length=255)
    broadcast_product = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'Product'


class BroadcastSchedule(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    broadcast_date = models.DateField()
    broadcast_time_start = models.TimeField()
    broadcast_time_end = models.TimeField()

    class Meta:
        managed = False
        db_table = 'BroadcastSchedule'


class BroadcastProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    product_video_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Broadcast_Product'


class HotdealProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    update_date = models.DateTimeField()
    cumulative_sales = models.IntegerField(blank=True, null=True)
    cumulative_dif = models.IntegerField(blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Hotdeal_Product'


class SimilarProduct(models.Model):
    similar_product_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    seller = models.CharField(max_length=255)
    product_url = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    product_image_url = models.CharField(max_length=255)
    price = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'SimilarProduct'


class Review(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    total_review = models.IntegerField()
    ratio = models.IntegerField()
    positive_review = models.CharField(max_length=255)
    negative_review = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'Review'
