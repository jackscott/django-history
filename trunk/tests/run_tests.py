from django.contrib.contenttypes.models       import ContentType
from django.contrib.modelhistory.models       import ChangeLog
from django.contrib.modelhistory.config       import debug_mode
from django.contrib.modelhistory.tests.models import TestModel

import cPickle as Pickle
import unittest
import decimal
import random


class TestModelHistory(unittest.TestCase):
    """
    A simple unittest.TestCase to coordinate existing tests
    into a more meaningful test battery.
    """

    def setUp(self):

        print "NOTE: You _must_ ensure that the relevant teset* model db tables are empty before\n"+\
              "      running these tests. The setUp method checks against the number of models and\n"+\
              "      changelog entries for sanity checking, and the table(s) must not otherwise be\n"+\
              "      filled.\n\n"+\
              "      ChangeLog checking is only done in debug_mode."
        
        print "\n*** Creating TestModel Objects ***"

        a = TestModel()
        a.unit_price = decimal.Decimal(str(random.uniform(0.0,100.0)))
        a.save()
        
        self.lowerBound = a.id

        # create dummy TestModels
        for i in range(1,10):
            a = TestModel()
            a.unit_price = decimal.Decimal(str(random.uniform(0.0,100.0)))
            a.save()

        models = TestModel.objects.all()
        self.assertEquals(len(models),10)

        print ">Done"
        print "\n*** Making Random Modifications ***"
            
        # just modify random models on
        # a whim for a sizable number of times
        models = TestModel.objects.all()
        num_iter = random.randint(75,150)
    
        for i in range(0,num_iter):
            a = models[random.randint(0,len(models)-1)]
            a.unit_price = decimal.Decimal(str(random.uniform(0.0,100.0)))
            a.save()

        logs = ChangeLog.objects.all()
        if not debug_mode:
            self.assertEquals(len(logs),len(models)+num_iter)
        else:
            print "Warning: number of ChangeLog entries will not be verified."

        print ">Done"

    def testRevert(self):

        print "\n*** Testing TestModel Reverting ***"

        testModel   = TestModel()
        contentType = ContentType.objects.get_for_model(testModel)
        models      = list()

        for i in range(1,10):
            models = TestModel.objects.all()

            if len(models) == 0:
                print "There are no TestModel objects"
                return
            elif len(models) == 1:
                model = models[0]
            else:
                model = models[random.randint(0,len(models)-1)]
                log = ChangeLog.objects.filter(content_type=contentType).filter(object_id=model.id)
                
            if len(log) == 0:
                print "There are no suitable ChangeLog objects."
                return
            elif len(log) == 1:
                version = 1
            else:
                version = random.randint(1,(len(log)-1))


            print "Reverting Random TestModel to Stored Object @rev %d" % (version)
            temp = ChangeLog.objects.filter(content_type=contentType).filter(object_id=model.id).\
                                    get(revision=version)
            tempObject = Pickle.loads(temp.object)
            print "TestModel (id=%d) Past (rev %d)\n%s" % (model.id,version,str(tempObject))

            logs = ChangeLog.objects.filter(content_type=contentType).filter(object_id=model.id)
            print "TestModel (id=%d) Current (rev %d)\n%s" % (model.id,len(logs),str(model))

            ChangeLog.objects.set_version(model,version)
            logs = ChangeLog.objects.filter(content_type=contentType).filter(object_id=model.id)
            print "TestModel (id=%d) Reverted (rev %d)\n%s" % (model.id,len(logs),\
                                                               str(TestModel.objects.get(id=model.id)))

            old_object = Pickle.loads(temp.object)
            new_object = TestModel.objects.get(id=model.id)

            self.assertEquals(old_object,new_object)

        print ">Done"

    def testReadLog(self):

        print "\n*** Testing TestModel Revision Histories ***"

        max = len(TestModel.objects.all())
        obj = TestModel.objects.get(id=self.lowerBound)
        revs = ChangeLog.objects.get_history(obj)

        print "Revision History for TestModel (id=%d)" % (obj.id)
        for rev in revs:
            print "Revision %d\n: %s" % (rev.get_revision(),rev.get_object())

        print ">Done"

    def testRestore(self):

        print "\n*** Testing Complete Restoration (Deleted Object) ***"

        max   = len(TestModel.objects.all())
        obj = TestModel.objects.get(id=self.lowerBound)
        revs  = ChangeLog.objects.get_history(obj)
        oid    = obj.id
        ctype = ContentType.objects.get(model="testmodel")

        print "Deleting TestModel (id=%d)" % (oid)
        
        obj.delete()
        rev = random.randint(1,len(revs)-1)
        obj = ChangeLog.objects.restore_version(ctype,oid,rev)
        obj.save()

        print "Restored TestModel (id=%d) to Revision %d" % (obj.id,rev)

        print ">Done"

    def tearDown(self):
        """
        Remove all the models and remove their revision history.
        """

        print "\n*** Deleting TestModel Objects ***"

        # Delete dummy TestModels
        models = TestModel.objects.all()
        for model in models:
            model.delete()

        if not debug_mode:

            # Delete their ChangeLog History
            logs = ChangeLog.objects.all()
            for log in logs:
                log.delete()

        print ">Done"


if __name__ == "__main__":
    unittest.main()
