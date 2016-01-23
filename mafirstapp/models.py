from django.db import models

class Author(models.Model):
	name = models.CharField(max_length=20)

class Book(models.Model):
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')
