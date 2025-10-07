# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Customer(models.Model):
    customer_code = models.CharField(primary_key=True, max_length=6)
    customer_name = models.CharField(max_length=32, blank=True, null=True)
    customer_telno = models.CharField(max_length=13, blank=True, null=True)
    customer_postalcode = models.CharField(max_length=8, blank=True, null=True)
    customer_address = models.CharField(max_length=40, blank=True, null=True)
    discount_rate = models.IntegerField(blank=True, null=True)
    delete_flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = "customer"


class CustomerNumbering(models.Model):
    customer_code = models.IntegerField()

    class Meta:
        managed = False
        db_table = "customer_numbering"


class Employee(models.Model):
    employee_no = models.CharField(primary_key=True, max_length=6)
    employee_name = models.CharField(max_length=32, blank=True, null=True)
    password = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "employee"


class Item(models.Model):
    item_code = models.CharField(primary_key=True, max_length=6)
    item_name = models.CharField(max_length=32, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "item"


class OrderDetails(models.Model):
    order_no = models.OneToOneField("Orders", models.DO_NOTHING, db_column="order_no", primary_key=True)  # The composite primary key (order_no, item_code) found, that is not supported. The first column is selected.
    item_code = models.ForeignKey(Item, models.DO_NOTHING, db_column="item_code")
    order_num = models.IntegerField(blank=True, null=True)
    order_price = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "order_details"
        unique_together = (("order_no", "item_code"),)


class Orders(models.Model):
    order_no = models.CharField(primary_key=True, max_length=6)
    customer_code = models.ForeignKey(Customer, models.DO_NOTHING, db_column="customer_code", blank=True, null=True)
    employee_no = models.ForeignKey(Employee, models.DO_NOTHING, db_column="employee_no", blank=True, null=True)
    total_price = models.IntegerField(blank=True, null=True)
    detail_num = models.IntegerField(blank=True, null=True)
    deliver_date = models.DateField(blank=True, null=True)
    order_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "orders"
