#!/usr/bin/python
# -*- coding: utf-8 -*-
# Bot to watch channels

import sys, os, re, time, string, threading, thread
import ConfigParser
#needs python-irclib
from ircbot import SingleServerIRCBot
from irclib import nm_to_n

class FreenodeBot(SingleServerIRCBot):
	def __init__(self, channel, nickname, server, password, port=6667):
		SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.server = server
		self.channel = channel
		self.nickname = nickname
		self.password = password
		self.version = '1.5'
		
	def on_error(self, c, e):
		print 'Error:\nArguments: %s\nTarget: %s' % (e.arguments(), e.target())
		self.die()
		sys.exit()
	
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")
		c.privmsg("NickServ",'GHOST %s %s' % (self.nickname, self.password))
		c.nick(self.nickname) #FIX
		c.privmsg("NickServ",'IDENTIFY %s' % self.password)

	def on_welcome(self, c, e):
		c.privmsg("NickServ",'GHOST %s %s' % (self.nickname, self.password))
		c.privmsg("NickServ",'IDENTIFY %s' % self.password)
		time.sleep(5)#let identification succeed before joining channels
		c.join(self.channel)

	def on_ctcp(self, c, e):
		if e.arguments()[0] == "VERSION":
			c.ctcp_reply(nm_to_n(e.source()),"Bot for watching stuff in " + self.channel)
		elif e.arguments()[0] == "PING":
			if len(e.arguments()) > 1: c.ctcp_reply(nm_to_n(e.source()),"PING " + e.arguments()[1])

	def on_action(self, c, e):
		timestamp = '[%s] ' % time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time()))
		nick = nm_to_n(e.source())
		who = '<%s/%s>' % (e.target(), nick)
		a = e.arguments()[0]
##        print timestamp+" * "+who+a
		
	def on_privmsg(self, c, e):
		timestamp = '[%s] ' % time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time()))
		nick = nm_to_n(e.source())
		target = nick
		who = '<%s/%s>' % (e.target(), nick)
		a = e.arguments()[0].split(":", 1)
		talkintome = False
		if a[0] == self.nickname:
			talkintome = True
		if not talkintome:
			if e.arguments()[0].lower().startswith("!steward"):
				bot1.msg('%s requested attention: %s' % (nick, ', '.join(config.get('Setup', 'optin').split('<|>'))), self.channel)
		else:
			if len(a) == 2:
				command = a[1].strip()
				if self.getCloak(e.source()) in config.get('Setup', 'privileged').split('<|>'):
					try:
						self.do_command(e, command, target)
					except:
						print 'Error: %s' % sys.exc_info()[1]
						self.msg('You have to follow the proper syntax. See \x0302[[m:User:Mike.lifeguard/DeSpamWatcher]]\x03.', nick)
		
	def on_pubmsg(self, c, e):
		timestamp = '[%s] ' % time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time()))
		nick = nm_to_n(e.source())
		target = e.target()
		who = '<%s/%s>' % (e.target(), nick)
		a = e.arguments()[0].split(":", 1)
		talkintome = False
		if a[0] == self.nickname:
			talkintome = True
		if not talkintome:
			if e.arguments()[0].lower().startswith("!admin") and self.nickname == nickname:
				self.msg('%s requested attention: %s' % (nick, ', '.join(config.get('Setup', 'optin').split('<|>'))), self.channel)
		else:
			if len(a) == 2:
				command = a[1].strip()
				if self.getCloak(e.source()) in config.get('Setup', 'privileged').split('<|>'):
					try:
						self.do_command(e, command, target)
					except:
						print 'Error: %s' % sys.exc_info()[1]
						self.msg('You have to follow the proper syntax. See \x0302[[m:User:Mike.lifeguard/DeSpamWatcher]]\x03.', nick)
			
	def do_command(self, e, cmd, target):
		nick = nm_to_n(e.source())
		c = self.connection
		args = cmd.split(' ')
		if args[0] == '_':
			args.remove('_')

		if args[0] == 'test':#Notifications
			self.msg('Testing.', nick)
		elif args[0] == 'help':
			self.msg(config.get('Setup', 'help'), nick)
		elif args[0] == 'report':#Set report levels
			if args[1] == 'list':
				message = ''
				for section in config.sections():
					if section != 'Setup':
						message += '%s: %s; ' % (section, config.get(section, 'report'))
				self.msg(message, target)
			elif args[1] == 'all':
				if args[2] == 'False':
					level = 'False'
				else:
					level = 'True'
				for section in config.sections():
					if section != 'Setup':
						self.setConfig(section, 'report', level)
				self.msg('Setting report level for all configured channels to %s.' % level, target)
			elif args[1] == 'deonly':
				for section in config.sections():
					if section != 'Setup' and section != '#de.wikipedia':
						self.setConfig(section, 'report', 'False')
				self.msg('Setting report level for all configured channels except #de.wikipedia to False.', target)
			elif config.has_section(args[1]):
				if args[2] == 'False':
					level = 'False'
				else:
					level = 'True'
				self.setConfig(args[1], 'report', level)
				self.msg('Setting report level for %s to %s.' % (args[1], level), target)
			else:
				self.msg('You have to specify a channel. Use irc.wikimedia.org\'s channel name, "all" or "enonly".', target)
		elif args[0] == 'list':#Lists: modify and show
			if args[1] == 'report':
				message = ''
				for section in config.sections():
					if section != 'Setup':
						message += '%s: %s; ' % (section, config.get(section, 'report'))
				self.msg(message, target)
			elif args[1] == 'privileged':
				self.msg('Privileged cloaks: %s' % ', '.join(config.get('Setup', 'privileged').split('<|>')), nick)
			elif args[1] == 'optin':
				self.msg('Admins: %s' % ', '.join(config.get('Setup', 'optin').split('<|>')), nick)
			elif args[1] == 'wiki':
				wikis = []
				for section in config.sections():
					if section != 'Setup':
						wikis.append(section)
				self.msg('Watching: %s' % ', '.join(wikis), target)
			elif args[2] == 'ignored':
				if config.has_section(args[1]):
					self.msg('Ignored users: %s' % ', '.join(config.get(args[1], 'ignored').split('<|>')), target)
			elif args[2] == 'stalked':
				if config.has_section(args[1]):
					stalked = config.get(args[1], 'stalked').split('<|>')
					self.msg('Stalked pages:', target)
					for p in stalked:
						self.msg(p, target)
		elif args[0] == 'add':
			if args[1] == 'privileged':
				who = ' '.join(args[2:])
				self.addToList(who, 'Setup', 'privileged', target)
			elif args[1] == 'optin':
				who = ' '.join(args[2:])
				self.addToList(who, 'Setup', 'optin', target)
			elif args[1] == 'wiki':
				newchannel = args[2]
				parse = re.compile(r"^#(?P<lang>\w+)\.(?P<family>\w+)$", re.IGNORECASE)
				lang = parse.search(newchannel).group('lang').lower()
				family = parse.search(newchannel).group('family').lower()
				if family == 'wikipedia':
					iwprefix = 'w:%s' % lang
				elif family == 'wikibooks':
					iwprefix = 'b:%s' % lang
				elif family == 'wikinews':
					iwprefix = 'n:%s' % lang
				elif family == 'wikiquote':
					iwprefix = 'q:%s' % lang
				elif family == 'wikisource':
					iwprefix = 's:%s' % lang
				elif family == 'wiktionary':
					iwprefix = 'wikt:%s' % lang
				elif family == 'wikiversity':
					iwprefix = 'v:%s' % lang
				elif lang == 'commons':
					iwprefix = 'commons'
				elif lang == 'meta':
					iwprefix = 'm'

				config.add_section(newchannel)
				self.setConfig(newchannel, 'ignored', '')
				self.setConfig(newchannel, 'domain', '%s.%s' % (lang, family))
				self.setConfig(newchannel, 'iwprefix', iwprefix)
				self.setConfig(newchannel, 'stalked', 'MediaWiki:Spam-blacklist<|>MediaWiki talk:Spam-blacklist')
				self.setConfig(newchannel, 'report', 'True')
				self.saveConfig()
				rcreader.connection.join(newchannel)
				self.msg('Monitoring %s' % newchannel, target)
			elif config.has_section(args[1]):
				if args[2] == 'ignored':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.addToList(who, args[1], 'ignored', target)
				elif args[2] == 'stalked':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.addToList(who, args[1], 'stalked', target)
		elif args[0] == 'remove':
			if args[1] == 'privileged':
				who = ' '.join(args[2:])
				self.removeFromList(who, 'Setup', 'privileged', target)
			if args[1] == 'optin':
				who = ' '.join(args[2:])
				self.removeFromList(who, 'Setup', 'optin', target)
			elif args[1] == 'wiki':
				#Removing is not possible, so set report to False
				if config.has_section(args[2]):
					self.setConfig(args[2], 'report', 'False')
					self.msg('This isn\'t working yet. However the report level for this channel has been set to False.', channel)
				else:
					self.msg('No such channel: %s.' % args[1], target)
			elif config.has_section(args[1]):
				if args[2] == 'ignored':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.removeFromList(who, args[1], 'ignored', target)
				elif args[2] == 'stalked':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.removeFromList(who, args[1], 'stalked', target)
		elif args[0] == 'huggle':#Huggle
			if args[1]:
				who = args[1]
				self.connection.action(self.channel, 'huggles ' + who)
			if not who:
				self.msg('lolfail', target)
		elif args[0] == 'die':#Die
			if self.getCloak(e.source()) not in config.get('Setup', 'owner').split('<|>'):
				self.msg('You can\'t kill me; you\'re not my owner!', nm_to_n(e.source()))
			else:
				print 'Yes, you\'re my owner.'
				if len(args)>=2:
					quitmsg = ' '.join(args[1:])
				else:
					quitmsg = config.get('Setup', 'quitmsg')
				self.saveConfig()
				print 'Saved config. Now killing all bots with message: "' + quitmsg + '"...'
				rawquitmsg = ':'+quitmsg
				bot1.connection.part(bot1.channel, rawquitmsg)
				bot1.connection.quit(rawquitmsg)
				bot1.disconnect()
				for section in config.sections():
					if section != 'Setup':
						rcreader.connection.part(section)
				rcreader.connection.quit()
				rcreader.disconnect()
				print 'Killed. Now exiting...'
				os._exit(os.EX_OK)

	def saveConfig(self):
		print 'saveConfig(self)'
		configFile = open(os.path.expanduser('~/Watchlist-bots/DeSpamWatcher.ini'), 'w')
		config.write(configFile)
		configFile.close()
		print 'done!'
			
	def setConfig(self, section, option, value):
		print 'setConfig(self, \'%s\', \'%s\', \'%s\')' % (section, option, value)
		config.set(section, option, value)

	def addToList(self, who, section, groupname, target):
		print 'addToLost(self, \'%s\', \'%s\', \'%s\', \'%s\')' % (who, section, groupname, target)
		if who == '' or who == ' ':
			return False
		list = config.get(section, groupname).split('<|>')
		if not who in list:
			list.append(who)
			list = '<|>'.join(list)
			self.setConfig(section, groupname, list)
			self.saveConfig()
			self.msg('%s added to %s.' % (who, groupname), target)

	def removeFromList(self, who, section, groupname, target):
		print 'removeFromList(self, \'%s\', \'%s\', \'%s\', \'%s\')' % (who, section, groupname, target)
		if who == '' or who == ' ':
			return False
		list = config.get(section, groupname).split('<|>')
		if who in list:
			list.remove(who)
			list = '<|>'.join(list)
			self.setConfig(section, groupname, list)
			self.saveConfig()
			self.msg('%s removed from %s.' % (who, groupname), target)

	def msg(self, message, target=None):
##        print 'msg(self, \'%s\', \'%s\')' % (message, target)
		if not target:
			target = self.channel
		self.connection.privmsg(target, message)
	
	def getCloak(self, doer):
		print 'getCloak(self, \'%s\')' % doer
		if re.search('@', doer):
			return doer.split('@')[1]

class WikimediaBot(SingleServerIRCBot):
	def __init__(self, channels, nickname, server, port=6667):
		SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.server = server
		self.channellist = channels
		self.nickname = nickname

	def on_error(self, c, e):
		print e.target()
		#self.die()
	
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + '_')

	def on_welcome(self, c, e):
		for channel in self.channellist:
			c.join(channel)

	def on_ctcp(self, c, e):
		if e.arguments()[0] == 'VERSION':
			c.ctcp_reply(nm_to_n(e.source()), 'Bot for watching stuff in ' + channel)
		elif e.arguments()[0] == 'PING':
			if len(e.arguments()) > 1: c.ctcp_reply(nm_to_n(e.source()),"PING " + e.arguments()[1])
		
	def on_pubmsg(self, c, e):
		timestamp = '[%s] ' % time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(time.time()))
		who = '<%s/%s> ' % (e.target(), nm_to_n(e.source()))
		a = (e.arguments()[0])
		nick = nm_to_n(e.source())
		
		if not config.has_section(e.target()):
			return
			
		if config.get(e.target(), 'report') == 'True':
			#Parsing the rcbot output
			comp = re.compile("\\x0314\[\[\\x0307(?P<page>.+?)\\x0314\]\](.+?)diff=(?P<diff>[0-9]+)&oldid=(.+?)\\x03 \\x035\*\\x03 \\x0303(?P<user>.+?)\\x03 \\x035\*\\x03 \((.+?)\) \\x0310(?P<comment>.*)\\x03", re.DOTALL)
			found = comp.search(a)
			if not found:
				return
			rcpage = found.group('page').strip(" ")
			watched = False
			for pg in config.get(e.target(), 'stalked').split('<|>'):
				if pg == rcpage:
					watched = True
					break
			if not watched:
				return
			rcuser = found.group('user').strip(" ")
			if rcuser in config.get(e.target(), 'ignored').split('<|>'):
				return
			#print timestamp+who+a
			rccomment = found.group('comment')
			rcdiff = found.group('diff')
			if not rccomment:
				comment=section=""
			else:
				comp = re.compile("/\* *(?P<section>.+?) *\*/", re.DOTALL)
				found = comp.search(rccomment)
				if found: section="#"+found.group('section')
				else: section=""
				rccomment=re.sub("/\*(.+?)\*/", "", rccomment.strip(" "))
				if rccomment.replace(" ", "") == "": comment=""
				else: comment=" \x0307(" + rccomment.strip(" ") + ")\x03"
			bot1.msg("\x0303%s\x03 edited \x0310[[:%s:%s%s]]\x03 \x0302http://%s/wiki/?diff=prev&oldid=%s\x03%s" % (rcuser, config.get(e.target(), 'iwprefix'), rcpage, section, config.get(e.target(), 'domain'),  rcdiff, comment))
			
class BotThread(threading.Thread):
	def __init__ (self, bot):
		self.b=bot
		threading.Thread.__init__ (self)

	def run (self):
		self.startbot(self.b)

	def startbot(self, bot):
		bot.start()

def main():  
	global bot1, rcreader, config
	config = ConfigParser.ConfigParser()
	config.read(os.path.expanduser('~/Watchlist-bots/DeSpamWatcher.ini'))
	nickname = config.get('Setup', 'nickname')
	password = config.get('Setup', 'password')
	mainchannel = config.get('Setup', 'channel')
	mainserver = config.get('Setup', 'server')
	wmserver = config.get('Setup', 'wmserver')
	channels = []
	for section in config.sections():
		if section != 'Setup':
			channels.append(section)
	
	bot1 = FreenodeBot(mainchannel, nickname, mainserver, password, 6667)
	BotThread(bot1).start()
	rcreader = WikimediaBot(channels, nickname, wmserver, 6667)
	BotThread(rcreader).start() #can cause ServerNotConnectedError

if __name__ == "__main__":
	global bot1, rcreader, config
#    main()
	try:
		main()
	except:
		print '\nUnexpected error: %s' % sys.exc_info()[1]
		bot1.die()
		rcreader.die()
		sys.exit()

