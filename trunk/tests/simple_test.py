from django.contrib.modelhistory.tests.models import TestModel2, TestModel3
from django.contrib.modelhistory.models       import ChangeLog
from django.contrib.contenttypes.models       import ContentType
import unittest

class TestChangeLog(unittest.TestCase):
    """
    """

    def testModel2(self):

        print "*** Testing non-revisioned model ..."

        m = TestModel2()
        m.dummy = 3
        m.save()
        
        m.dummy = 16
        m.save()

        m.delete()

        ct = ContentType.objects.get(model="testmodel2")
        logs = ChangeLog.objects.filter(content_type=ct).\
               filter(object_id=m.id)
        self.assertEqual(len(logs),0)

    def testModel3(self):

        print "*** Testing non-revisioned model ..."
            
        m = TestModel3()
        m.dummy = 3
        m.save()
            
        m.dummy = 16
        m.save()

        ChangeLog.objects.set_version(m,1)

        mid = m.id
        m.delete()

        ct = ContentType.objects.get(model="testmodel3")
        ChangeLog.objects.restore_version(ct,mid,1)

        logs = ChangeLog.objects.filter(content_type=ct).\
               filter(object_id=mid)
        self.assertEqual(len(logs),5)


if __name__ == "__main__":
    unittest.main()
