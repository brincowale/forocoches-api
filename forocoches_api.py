# -*- coding: utf-8 -*-
from grab import Grab
import time


class ForocochesAPI:

    def __init__(self, username, password):
        self.g = Grab()
        self.login(username, password)

    def login(self, username, password):
        """
        Login and keep session opened
        :param username: username of account
        :param password: password of account
        :return: raise and error if user can't login
        """
        g = self.g
        g.go('https://m.forocoches.com/foro/misc.php?do=page&template=ident')
        g.doc.set_input('vb_login_username', username)
        g.doc.set_input('vb_login_password', password)
        g.doc.submit()
        if 'Usuario y contrase&ntilde;a equivocados' in g.response.body:
            raise LoginError('User not logged in')

    def publish_message(self, thread_id, message):
        """
        Publish a message in a thread
        :param thread_id: a string with the identifier of tread
        :param message: a string with text to publish
        :return: True when message has been published, otherwise raise an exception
        """
        g = self.g
        g.go('https://m.forocoches.com/foro/showthread.php?t=' + thread_id)
        try:
            g.doc.set_input('message', message)
        except Exception:
            raise ValueError('Unknown error when trying to reply')
        g.doc.submit()
        # if an error occurred, raise a custom exception
        if g.doc.text_search(u'Este mensaje es un duplicado de otro mensaje que ha sido creado'):
            raise DuplicatedMessageError('Mensaje duplicado en los útimos 5 minutos')
        elif g.doc.text_search(u'Debes esperar al menos 30 segundos entre cada envio de nuevos mensajes'):
            raise TooManyMessagesError('Solo puedes enviar mensajes cada 30 segundos')
        elif g.doc.text_search(u'Los siguientes errores ocurrieron al enviar este mensaje')\
                or g.doc.text_search(u'ForoCoches - Responder al Tema'):
            raise PublishError('Ha ocurrido un error al publicar el mensaje')
        # parameter p is the post id, only appears if the message was published
        elif '?p=' in g.response.url or '&p=' in g.response.url:
            return True
        else:
            raise PublishError('Ha ocurrido un error desconocido')

    def publish_message_automatically(self, thread_id, message, retry=5, wait_seconds=30):
        """
        Publish a message in a specified thread. If reply fail, retry up to the maximum desired retries.
        :param thread_id: a string with the identifier of tread
        :param message: a string with text to publish
        :param retry: the maximum times to retry
        :param wait_seconds: the time in seconds to wait before try to reply again
        :return: True when the message has been published, False otherwise
        """
        i = 0
        while i < retry:
            try:
                self.publish_message(thread_id, message)
                return True
            except:
                time.sleep(wait_seconds)
                i += 1
        return False


class DuplicatedMessageError(LookupError):
    """raise this when a message is a duplicated of other in less than 5 minutes"""


class TooManyMessagesError(LookupError):
    """raise this when other message has sent in less than 30 seconds"""


class PublishError(LookupError):
    """raise this when
     an unknown error occurred trying to publish the message"""


class LoginError(LookupError):
    """raise this when a login failed"""
