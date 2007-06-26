from django.dispatch                    import dispatcher
from django.db.models                   import signals
from django.contrib.contenttypes        import generic
from django.contrib.modelhistory.config import debug_mode
from datetime                           import datetime

import cPickle as Pickle
import inspect


def new_revision_save(sender, instance, signal, *args, **kwargs):
    """
    Wrapper function for new_revision() for post_save signal.
    """

    new_revision(sender, instance, signal, signal_name='post_save', *args, **kwargs)

def new_revision_delete(sender, instance, signal, *args, **kwargs):
    """
    Wrapper function for new_revision() for pre_delete signal.
    """

    new_revision(sender, instance, signal, signal_name='pre_delete', *args, **kwargs)

def new_revision(sender, instance, signal, signal_name, *args, **kwargs):
    """ 
    Handles the bookkeeping for all 'History'-enabled objects.

    If 'signal_name' is 'pre_delete', an object deletion has been requested and we
    must save the last known state of 'instance'.

    If 'signal_name' is 'post_save' and len(possibleRevisions) is 0, an object has
    just been created and should be recorded appropriately.

    If 'signal_name' is 'post_save' and len(possibleRevisions) is greater than 0,
    an object model has been modified and this event should also be recorded.

    Note that 'pre_save' is not used as we will not have the model instance's
    primary key until _after_ the save method has completed.
    """

    from django.contrib.contenttypes.models import ContentType
    from django.contrib.modelhistory.models import ChangeLog
    from django.contrib.auth.models         import User


    # Allow Only Revisioned Models
    if instance.__class__.__name__ is 'ChangeLog' or not hasattr(instance, 'History'): 
        if debug_mode:
            print "Type %s is not configured to be a revisioned model." %\
                  (instance.__class__.__name__)
        return 0

    # Determine User
    user = snoop_the_call_chain()
    if user:
        print "AUDIT: User Account %s initiated model mutation." % (str(user))
    else:
        try:
            user = User.objects.get(username="audit")
        except User.DoesNotExist:
            user = User(username="audit",\
                        first_name="Auditing",\
                        last_name="Account",\
                        email="audit@foobar.com")
            user.set_password('password')
            user.save()

    # Handle Accounting
    try:
            
        # Calculate the number of current revision entries for this object.
        contentType    = ContentType.objects.get_for_model(instance)
        totalRevisions = ChangeLog.objects.filter(object_id=instance.id).filter(\
                                                      content_type=contentType)

        if signal_name is 'pre_delete':

            try:

                log = ChangeLog(parent=instance, change_type='D',\
                                revision=len(totalRevisions)+1)
                log.object = Pickle.dumps(None)
                log.user = user
                log.save()

            except Exception, e:
                print "Saving new revision failed for object type %s: %s" %\
                      (instance.__class__.__name__,str(e))

        elif signal_name is 'post_save':

            try:

                if len(totalRevisions) == 0:
                    log = ChangeLog(parent=instance, change_type='A',\
                                    revision=1)
                else:
                    log = ChangeLog(parent=instance, change_type='U',\
                                    revision=len(totalRevisions)+1)

                log.object = Pickle.dumps(instance)
                log.user = user
                log.save()

            except Exception, e:
                print "Saving new revision failed for object type %s: %s" %\
                      (instance.__class__.__name__,str(e))

        else:
            # NOTE: In general, should be because instance is without an ID.
            print "Type %s is cannot be(become) a revisioned model: Model "+\
                  "has None id (default primary key)." %\
                  (instance.__class__.__name__)

    except Exception, e:
        raise("Exception in save_new_revision: %s" %(str(e)))
        

def snoop_the_call_chain():
    """
    Currently, a hackish (and a bit naive) way of walking up the call chain
    to determine the user (if any) that initiated the change in the system.
    """

    from django.contrib.auth.models         import User

    cur = inspect.currentframe()
    desiredFrame = None
    desiredFrameCount = 0
    f = None

    try:
        ancestors = inspect.getouterframes(cur)
        count = 0
        for frame in ancestors:
            if frame[3] == "save":
                desiredFrameCount = count
            count = count+1

        # Ensure that we have a callee for the save methods
        # which we're auditing.
        if debug_mode: print "Desired Frame: (%d)\n" % (desiredFrameCount+1)
        if desiredFrameCount >= len(ancestors):
            if debug_mode: print "No callee in call chain for save method. Bailing ..."
            return None

        desiredFrame = ancestors[desiredFrameCount+1][0]
        if inspect.isframe(desiredFrame):
            for name,value in inspect.getmembers(desiredFrame):
                if name == "f_locals":

                    dictionary = dict(value)
                    count = 1
                    if debug_mode: print "=========== Begin Frame Objects ==============="
                    for key,val in dictionary.items():
                        if debug_mode: print "   (%d) %s: %s" % (count,key,val)
                        count = count + 1
                    if debug_mode: print "============ End Frame Objects ================\n"
                       
                    if 'request' in dictionary.keys() and\
                           dictionary['request'].user:
                            
                        if debug_mode: print "*** Found Calling User ***"
                        return dictionary['request'].user

    finally:
        del cur


#
# SIGNAL HANDLER BINDINGS
#

dispatcher.connect( new_revision_save,   signal=signals.post_save )
dispatcher.connect( new_revision_delete, signal=signals.pre_delete )

if debug_mode:
    print "Attaching %s to signals.post_save" % (new_revision_save)
    print "Attaching %s to signals.pre_delete" % (new_revision_delete)
