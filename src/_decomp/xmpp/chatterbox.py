#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\xmpp\chatterbox.py
import random
import socket
import ssl
import logging
import uthread2
logger = logging.getLogger(__name__)
PHRASES = ['Today a man knocked on my door and asked for a small donation towards the local swimming pool. I gave him a glass of water.',
 'A recent study has found that women who carry a little extra weight live longer than the men who mention it.',
 "Life is all about perspective. The sinking of the Titanic was a miracle to the lobsters in the ship's kitchen.",
 "You know that tingly little feeling you get when you like someone? That's your common sense leaving your body.",
 "I'm great at multitasking. I can waste time, be unproductive, and procrastinate all at once.",
 'If i had a dollar for every girl that found me unattractive, they would eventually find me attractive.',
 'I want to die peacefully in my sleep, like my grandfather.. Not screaming and yelling like the passengers in his car.',
 'My wife and I were happy for twenty years. Then we met.',
 "Isn't it great to live in the 21st century? Where deleting history has become more important than making it.",
 'I find it ironic that the colors red, white, and blue stand for freedom until they are flashing behind you.',
 "Just read that 4,153,237 people got married last year, not to cause any trouble but shouldn't that be an even number?",
 'Relationships are a lot like algebra. Have you ever looked at your X and wondered Y?',
 "Life is like toilet paper, you're either on a roll or taking shit from some asshole.",
 "Apparently I snore so loudly that it scares everyone in the car I'm driving.",
 'When wearing a bikini, women reveal 90 % of their body... men are so polite they only look at the covered parts.',
 "I can totally keep secrets. It's the people I tell them to that can't.",
 'Alcohol is a perfect solvent: It dissolves marriages, families and careers.',
 "Strong people don't put others down. They lift them up and slam them on the ground for maximum damage.",
 "I like to finish other people's sentences because... my version is better.",
 "When my boss asked me who is the stupid one, me or him? I told him everyone knows he doesn't hire stupid people.",
 'Hi!',
 "What's up?",
 'Hello',
 'Wazzup?',
 'Dude!',
 'Yo!',
 "I'm here!",
 'Howdy!',
 'Greetings',
 "Let's jump!",
 "Shoot'em'all!",
 '42']

class ChatterBox(object):

    def __init__(self):
        self.socket = None
        self.stop_requested = False

    def start(self, use_tasklets = False, use_ssl = False):
        self.socket = socket.socket()
        if use_ssl:
            self.socket = ssl.wrap_socket(self.socket)
        self.socket.connect(('localhost', 8888))
        self.stop_requested = False
        if use_tasklets:
            self.talker = uthread2.start_tasklet(self._talker)
            self.listener = uthread2.start_tasklet(self._listener)
        else:
            self.worker = uthread2.start_tasklet(self._worker)

    def stop(self):
        self.stop_requested = True

    def _worker(self):
        while not self.stop_requested:
            phrase = random.choice(PHRASES)
            self.socket.sendall(phrase)
            print self.socket.recv(1024)
            uthread2.Sleep(1)

    def _listener(self):
        try:
            while not self.stop_requested:
                logger.debug('Waiting for data')
                data = self.socket.recv(4096)
                print data
                logger.debug('Received: %s', data)

        except Exception:
            logger.exception('Exception in listener %s', repr(self.listener.tasklet))
            raise

    def _talker(self):
        try:
            while not self.stop_requested:
                phrase = random.choice(PHRASES)[:16]
                logger.debug('Sending %s', phrase)
                print ('Sending', phrase)
                self.socket.sendall(phrase)
                logger.debug('Sleeping for 1 second')
                uthread2.Sleep(1)

        except Exception:
            logger.exception('Exception in talker %s', repr(self.talker.tasklet))
            raise
