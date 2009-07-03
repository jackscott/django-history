from django.contrib.auth.models         import User
from django.contrib.modelhistory.config import debug_mode
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes        import generic
from django.db                          import models
from django.utils.translation           import ugettext
from django.core.serializer              import serialize, deserialize 
from datetime import datetime
#import cPickle as Pickle


CHANGE_TYPES = (
    ('A', 'Added'),
    ('U', 'Updated'),
    ('D', 'Deleted'),
    ('R', 'Reverted'),
)

class ChangeLogManager(models.Manager):
    """
    Exposes common operations on the collection of
    all revisioned objects (ChangeLog instances).
    """

    def get_version(self, object, rev):
        """
        Returns a ChangeLog instance that corresponds
        to the stored object 'object' at revision
        'rev'.

        If no match is found, returns None.
        """

        ct = ContentType.objects.get_for_model(object)

        try:
            return self.get_query_set().filter(\
                content_type=ct.id).filter(\
                object_id=object.id).get(\
                revision=rev)

        except ChangeLog.DoesNotExist, e:
            return None

    def get_version_by_date(self, object, date):
        """ 
        Returns a list of revisions of object having
        occured at date.

        If no matches are found, returns an empty list.
        """

        ct = ContentType.objects.get_for_model(object)
        revisions = self.get_query_set().filter(
                        content_type=ct.id).filter(
                        change_time__exact=date)

        if len(history) > 0:
            return revisions
        else:
            return list()

    def get_history(self, object, offset=0):
        """ 
        Returns the last 'offset' revision(s) of object.

        If offset is not supplied, a list of all
        the revisions of object are returned.

        If no matches are found, return an empty list.
        """
        
        ct      = ContentType.objects.get_for_model(object)
        history = self.get_query_set().filter(\
                      content_type=ct.id).filter(\
                      object_id=object.id)

        if len(history) > 0 and len(history) > offset:
            return history[(-1*offset):]
        elif len(history) <= offset:
            return history
        else:
            return list()

    def set_version(self, object, rev):
        """
        Restores object given by 'object' with the stored
        instance given by a ChangeLog object with matching
        content_type, object_id and revision 'rev'.
        """

        ct = ContentType.objects.get_for_model(object)
        return self.__revert_to_version(ct,object.id,rev)

    def restore_version(self, content_type, object_id, rev):
        """
        Restores a previously deleted object by resurrecting
        the state of the object at revision from a stored
        object instance.
        """

        return self.__revert_to_version(content_type,object_id,rev)

    def __revert_to_version(self, ctype, obj_id, rev):
        """
        Private method that handles the details of restoring
        an object given by (content_type,object_id) using
        serialized object instances.
        """

        try:
            # Reload stored object at revision 'rev'
            revertFrom = self.get_query_set().filter(\
                content_type=ctype.id).filter(\
                object_id=obj_id).get(\
                revision=rev)
            #revertObject = Pickle.loads(revertFrom.object)
            revertObject = deserialize('json', reverFrom.object)
            revertObject.save()

            # Denote revert source revision
            logs = ChangeLog.objects.filter(\
                content_type=ctype.id).filter(\
                object_id=obj_id)
            latestRevision = logs[len(logs)-1]
            latestRevision.revert_from = rev
            latestRevision.change_type = 'R'
            latestRevision.save()

            return revertObject

        except ChangeLog.DoesNotExist, e:
            print "Requested revision does not exist: ", str(e)
            return None

        except Exception, e:
            print "Exception in __revert_to_version: ", str(e)
            return None

class ChangeLog(models.Model):
    """
    Implements simple revision control for Django models. Maintains
    serialized copies of all object instances by employing Django signals.

    Performs bookkeeping on all calls to save() and delete().
    """
    
    change_time  = models.DateTimeField (ugettext('Time of Change'), auto_now=True)
    content_type = models.ForeignKey(ContentType)
    parent       = generic.GenericForeignKey()
    object_id    = models.IntegerField(ugettext('Object ID'))
    user         = models.ForeignKey(User, default="1")
    change_type  = models.CharField(max_length=1, choices=CHANGE_TYPES)
    object       = models.TextField()
    revision     = models.PositiveIntegerField()
    revert_from  = models.PositiveIntegerField(default=0)

    objects      = ChangeLogManager()

    class Meta:
        verbose_name = ugettext('Change Log Entry')
        verbose_name_plural = ugettext('Change Log Entries')
        db_table = ugettext('django_history_log')

    def __unicode__(self):
        return "ChangeLog: " + str(self.get_object())

    def get_object(self):
        """
        Returns unpickled object.
        """
        #return Pickle.loads( str(self.object))
        return serialize('json', self.object )

    def get_revision(self):
        """
        Returns the revision number of ChangeLog
        entry's stored object.
        """

        return self.revision

    def get_field_dict(self):
        """
        Returns a dictionary mapping field names to field values in this version
        of the model.
        
        This method will follow parent links, if present.

        Borrowed from django-reversion (http://code.google.com/p/django-reversion/)
        """
        if not hasattr(self, "_field_dict_cache"):
            object_version = self.object_version
            obj = object_version.object
            result = {}
            for field in obj._meta.fields:
                result[field.name] = field.value_from_object(obj)
            result.update(object_version.m2m_data)
            # Add parent data.
            for parent_class, field in obj._meta.parents.items():
                content_type = ContentType.objects.get_for_model(parent_class)
                parent_id = unicode(getattr(obj, field.attname))
                try:
                    parent_version = Version.objects.get(revision__id=self.revision_id,
                                                         content_type=content_type,
                                                         object_id=parent_id)
                except parent_class.DoesNotExist:
                    pass
                else:
                    result.update(parent_version.get_field_dict())
            setattr(self, "_field_dict_cache", result)
        return getattr(self, "_field_dict_cache")
       
    field_dict = property(get_field_dict,
                          doc="A dictionary mapping field names to field values in this version of the model.")
