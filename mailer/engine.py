from __future__ import unicode_literals

import time
import smtplib
import logging

import lockfile
from socket import error as socket_error


from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import get_connection

from .models import (
 MessageLog, RESULT_SUCCESS, RESULT_FAILURE, Mail)
import mailbox


def mailbox_save(email):
    mbox = mailbox.Maildir('sendet1')
    mbox.add(email.message())
    mbox.flush()



# when queue is empty, how long to wait (in seconds) before checking again
EMPTY_QUEUE_SLEEP = getattr(settings, "MAILER_EMPTY_QUEUE_SLEEP", 300)

# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "MAILER_LOCK_WAIT_TIMEOUT", -1)

# allows for a different lockfile path. The default is a file
# in the current working directory.
LOCK_PATH = getattr(settings, "MAILER_LOCK_PATH", None)


def acquire_lock():
    logging.debug("acquiring lock...")
    if LOCK_PATH is not None:
        lock_file_path = LOCK_PATH
    else:
        lock_file_path = "send_mail"

    lock = lockfile.FileLock(lock_file_path)

    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except lockfile.AlreadyLocked:
        logging.debug("lock already in place. quitting.")
        print("lock already in place. quitting.")
        return False, lock
    except lockfile.LockTimeout:
        print("waiting for the lock timed out. quitting.")
        logging.debug("waiting for the lock timed out. quitting.")
        return False, lock
    logging.debug("acquired.")
    return True, lock


def release_lock(lock):
    logging.debug("releasing lock...")
    lock.release()
    logging.debug("released.")


def _require_no_backend_loop(mailer_email_backend):
    if mailer_email_backend == settings.EMAIL_BACKEND == 'mailer.backend.DbBackend':
        raise ImproperlyConfigured('EMAIL_BACKEND and MAILER_EMAIL_BACKEND'
                                   ' should not both be set to "{}"'
                                   ' at the same time'
                                   .format(settings.EMAIL_BACKEND))


def send_all():
    """
    Send all eligible messages in the queue.
    """
    # The actual backend to use for sending, defaulting to the Django default.
    # To make testing easier this is not stored at module level.
    mailer_email_backend = getattr(
        settings,
        "MAILER_EMAIL_BACKEND",
        "django.core.mail.backends.smtp.EmailBackend"
    )

    _require_no_backend_loop(mailer_email_backend)


    acquired, lock = acquire_lock()
    if not acquired:
        return
    start_time = time.time()

    deferred = 0
    sent = 0
    try:
        connection = None

        mails = Mail.objects.filter(status="4")
        for message in mails:

            try:
                if connection is None:
                    connection = get_connection(backend=mailer_email_backend)
                logging.info("sending message '{0}' to {1}".format(
                    message.title,
                    ", ".join(str(x) for x in message.to.all()))
                )
                email = message.create_email()
                if email is not None:
                    email.connection = connection
                    if not hasattr(email, 'reply_to'):
                        # Compatability fix for EmailMessage objects
                        # pickled when running < Django 1.8 and then
                        # unpickled under Django 1.8
                        email.reply_to = []
                    email.send()

                    # connection can't be stored in the MessageLog
                    message.logs.add(MessageLog.objects.log(message, RESULT_SUCCESS))
                    message.status = RESULT_SUCCESS
                    sent += 1
                    mailbox_save(email)
                else:
                    logging.warning("message discarded due to failure in converting from DB. Added on '%s' with priority '%s'" % (message.when_added, message.priority))  # noqa
                message.status = RESULT_SUCCESS

            except (socket_error, smtplib.SMTPSenderRefused,
                    smtplib.SMTPRecipientsRefused,
                    smtplib.SMTPDataError,
                    smtplib.SMTPAuthenticationError) as err:
                logging.info("message deferred due to failure: %s" % err)
                message.logs.add(MessageLog.objects.log(message, RESULT_FAILURE, log_message=str(err)))

                # Get new connection, it case the connection itself has an error.
                connection = None

            # Check if we reached the limits for the current run

    finally:
        release_lock(lock)

    logging.info("")
    logging.info("%s sent; %s deferred;" % (sent, deferred))
    logging.info("done in %.2f seconds" % (time.time() - start_time))


def send_loop():
    """
    Loop indefinitely, checking queue at intervals of EMPTY_QUEUE_SLEEP and
    sending messages if any are on queue.
    """

    while True:
        while not Message.objects.all():
            logging.debug("sleeping for %s seconds before checking queue again" % EMPTY_QUEUE_SLEEP)
            time.sleep(EMPTY_QUEUE_SLEEP)
        send_all()
