from django.db import models

class TestModel(models.Model):
    """
    """

    unit_price = models.DecimalField(max_digits=9,decimal_places=3)

    class History:
        pass

    def __str__(self):
        string = "TestModel object: \n"
        string = string + "*             id: %s\n" % (self.id)
        string = string + "*     unit_price: %s\n" % (self.unit_price)

        return string

    class Meta:
        db_table = 'test_model'

    class Admin:
        pass

class TestModel2(models.Model):
    """
    """

    dummy = models.IntegerField()

    def __str__(self):
        string = "TestModel object: \n"
        string = string + "*             id: %s\n" % (self.id)
        string = string + "*          dummy: %s\n" % (self.dummy)

        return string

    class Meta:
        db_table = 'test_model2'

    class Admin:
        pass

class TestModel3(models.Model):
    """
    """

    dummy = models.IntegerField()

    def __str__(self):
        string = "TestModel object: \n"
        string = string + "*             id: %s\n" % (self.id)
        string = string + "*          dummy: %s\n" % (self.dummy)

        return string

    class Meta:
        db_table = 'test_model3'

    class Admin:
        pass

    class History:
        pass
