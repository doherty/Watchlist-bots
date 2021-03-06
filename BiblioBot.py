#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# SYNPOPSIS:	This bot parses the RC feed for some projects, and reports to freenode
# LICENSE:		GPL
# CREDITS:		Mike.lifeguard, Erwin, Dungodung (Filip Maljkovic)
#

import sys, os, re, time, string, threading, thread, math
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
			if e.arguments()[0].lower().startswith("!admin"):
				bot1.msg('%s requested attention: %s' % (nick, ', '.join(config.get('Setup', 'optin').split('<|>'))), self.channel)
		else:
			if len(a) == 2:
				command = a[1].strip()
				if self.getCloak(e.source()) in config.get('Setup', 'privileged').split('<|>'):
					try:
						self.do_command(e, command, target)
					except:
						print 'Error: %s' % sys.exc_info()[1]
						self.msg('You have to follow the proper syntax. See \x0302http://toolserver.org/~stewardbots/IRC-watchbot\x03', nick)

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
			if e.arguments()[0].lower().startswith("!admin"):
				self.msg('%s requested attention: %s' % (nick, ', '.join(config.get('Setup', 'optin').split('<|>'))), self.channel)
		else:
			if len(a) == 2:
				command = a[1].strip()
				if self.getCloak(e.source()) in config.get('Setup', 'privileged').split('<|>'):
					try:
						self.do_command(e, command, target)
					except:
						print 'Error: %s' % sys.exc_info()[1]
						self.msg('You have to follow the proper syntax. See \x0302http://toolserver.org/~stewardbots/IRC-watchbot\x03', nick)

	def do_command(self, e, cmd, target):
		nick = nm_to_n(e.source())
		c = self.connection
		args = cmd.split(' ')
		if args[0] == '_':
			args.remove('_')

		if args[0] == 'test' or args[0] == 'prueba':#Notifications
			self.msg('Prueba.', nick)
		elif args[0] == 'help' or args[0] == 'ayuda':
			self.msg(config.get('Setup', 'help'), nick)
		elif args[0] == 'report' or args[0] == 'reporta':#Set report levels
			if args[1] == 'list' or args[1] == 'lista':
				message = ''
				for section in config.sections():
					if section != 'Setup':
						message += '%s: %s; ' % (section, config.get(section, 'report'))
				self.msg(message, target)
			elif args[1] == 'all' or args[1] == 'todo':
				if args[2] == 'False':
					level = 'False'
				else:
					level = 'True'
				for section in config.sections():
					if section != 'Setup':
						self.setConfig(section, 'report', level)
				self.msg('Seleccionando el nivel de reporte para todos canales configurados a %s.' % level, target)
			elif args[1] == 'esonly':
				for section in config.sections():
					if section != 'Setup' and section != '#es.wikipedia':
						self.setConfig(section, 'report', 'False')
				self.msg('Seleccionando el nivel de reporte para todos los canales configurados excepto #es.wikipedia a No.', target)
			elif config.has_section(args[1]):
				if args[2] == 'False':
					level = 'False'
				else:
					level = 'True'
				self.setConfig(args[1], 'report', level)
				self.msg('Seleccionando el nivel de reporte para %s a %s' % (args[1], level), target)
			else:
				self.msg('Tiene que especificar un canal. Use el nombre del canal irc.wikimedia.org, "all" or "esonly".', target)
		elif args[0] == 'list' or args[0] == 'lista':#Lists: modify and show
			if args[1] == 'report' or args[1] == 'reporta':
				message = ''
				for section in config.sections():
					if section != 'Setup':
						message += '%s: %s; ' % (section, config.get(section, 'report'))
				self.msg(message, target)
			elif args[1] == 'privileged' or args[1] == 'privilegiado':
				self.msg('Cloacks con acceso al bot: %s' % ', '.join(config.get('Setup', 'privileged').split('<|>')), nick)
			elif args[1] == 'optin':
				self.msg('Admins: %s' % ', '.join(config.get('Setup', 'optin').split('<|>')), nick)
			elif args[1] == 'wiki':
				wikis = []
				for section in config.sections():
					if section != 'Setup':
						wikis.append(section)
				self.msg('Monitorizando: %s' % ', '.join(wikis), target)
			elif args[1] == 'ignored' or args[1] == 'ignorado':
				if config.has_section(args[2]):
					self.msg('Usuarios ignorados: %s' % ', '.join(config.get(args[2], 'ignored').split('<|>')), target)
			elif args[1] == 'stalked' or args[1] == 'monitorizado':
				if config.has_section(args[2]):
					pages = config.get(args[2], 'stalked').split('<|>')
					if len(pages) != 0:
						shortlists = ['']
						index = 0
						maxlen = 400
						print pages
						for page in pages:
							print shortlists
							if len(shortlists[index]) + len(page) < maxlen:
								#append to the string at index
								if len(shortlists[index]) > 1:#if there's stuff there already, we want a comma
									shortlists[index]+=', '+page
								else:
									shortlists[index]+=page
							else:
								#increment index and then append there
								shortlists.append('')
								index+=1
								print index
								shortlists[index]+=page
						print 'done first for loop'
						for l in range(0, len(shortlists)):
							self.msg(r'Páginas monitorizadas (%s/%s): %s.' % (l+1, len(shortlists), shortlists[l]), target)
							time.sleep(2)#sleep a bit to avoid flooding?
		elif args[0] == 'add' or args[0] == 'añade':
			if args[1] == 'privileged' or args[1] == 'privilegiado':
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
				if args[2] == 'ignored' or args[2] == 'ignorado':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.addToList(who, args[1], 'ignored', target)
				elif args[2] == 'stalked' or args[2] == 'monitorizado':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.addToList(who, args[1], 'stalked', target)
		elif args[0] == 'remove' or args[0] == 'quita':
			if args[1] == 'privileged' or args[1] == 'privilegiado':
				who = ' '.join(args[2:])
				self.removeFromList(who, 'Setup', 'privileged', target)
			if args[1] == 'optin':
				who = ' '.join(args[2:])
				self.removeFromList(who, 'Setup', 'optin', target)
			elif args[1] == 'wiki':
				#Removing is not possible, so set report to False
				if config.has_section(args[2]):
					self.setConfig(args[2], 'report', 'False')
					self.msg('Eso todavía no está funcionando, De todos modos el nivel de reporte para este canal ha sido programado a No.', target)
				else:
					self.msg('Dicho canal no existe: %s.' % args[1], target)
			elif config.has_section(args[1]):
				if args[2] == 'ignored' or args[2] == 'ignorado':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.removeFromList(who, args[1], 'ignored', target)
				elif args[2] == 'stalked' or args[2] == 'monitorizado':
					who = ' '.join(args[3:])
					who = who[:1].upper()+who[1:]
					self.removeFromList(who, args[1], 'stalked', target)
		elif args[0] == 'huggle':#Huggle
			if args[1]:
				who = args[1]
				self.connection.action(self.channel, 'huggles ' + who)
			if not who:
				self.msg('lolfail', target)
		elif cmd.startswith('die'):#Die
			if self.getCloak(e.source()) not in config.get('Setup', 'owner').split('<|>'):
				self.msg('You can\'t kill me; you\'re not my owner!', nm_to_n(e.source()))
			else:
				print 'Yes, you\'re my owner.'
				if cmd == 'die':
					quitmsg = config.get('Setup', 'quitmsg')
				else:
					parse = re.compile(r"^die (?P<quitmsg>.*)$", re.IGNORECASE)
					quitmsg = parse.search(cmd).group('quitmsg').strip()
				rawquitmsg = ':'+quitmsg
				self.saveConfig()
				print 'Saved config. Now killing all bots with message: "%s"...' % quitmsg
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
		elif cmd.startswith('restart'):
			if self.getCloak(e.source()) not in config.get('Setup', 'owner').split('<|>'):
				self.msg('You can\'t restart me; you\'re not my owner!', target)
			else:
				print 'Yes, you\'re my owner'
				self.saveConfig()
				print 'Saved config for paranoia.'
				if cmd == 'restart':
					quitmsg = config.get('Setup', 'quitmsg')
					print 'Restarting all bots with message: '+quitmsg
					rawquitmsg = ':'+quitmsg
					try:
						for section in config.sections():
							if section != 'Setup':
								rcreader.connection.part(section)
						rcreader.connection.quit()
						rcreader.disconnect()
						BotThread(rcreader).start()
					except:
						print 'rcreader didn\'t recover: %s' % sys.exc_info()[1]
					try:
						bot1.connection.part(mainchannel, rawquitmsg)
						bot1.connection.quit()
						bot1.disconnect()
						BotThread(bot1).start()
					except:
						print 'bot1 didn\'t recover: %s' % sys.exc_info()[1]
				elif cmd == 'restart rc':
					self.msg('Restarting rc reader', target)
					try:
						for section in config.sections():
							if section != 'Setup':
								rcreader.connection.part(section)
						rcreader.connection.quit()
						rcreader.disconnect()
						BotThread(rcreader).start()
					except:
						print 'rcreader didn\'t recover: %s' % sys.exc_info()[1]

	def saveConfig(self):
		print 'saveConfig(self)'
		configFile = open(os.path.expanduser('~/Watchlist-bots/BiblioBot.ini'), 'w')
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
##		print 'msg(self, \'%s\', \'%s\')' % (message, target)
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
			bot1.msg("\x0303%s\x03 edited \x0310[[:%s:%s%s]]\x03 \x0302http://%s/wiki/?diff=%s\x03%s" % (rcuser, config.get(e.target(), 'iwprefix'), rcpage, section, config.get(e.target(), 'domain'),  rcdiff, comment))

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
	config.read(os.path.expanduser('~/Watchlist-bots/BiblioBot.ini'))
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
#	main()
	try:
		main()
	except:
		print '\nUnexpected error: %s' % sys.exc_info()[1]
		bot1.die()
		rcreader.die()
		sys.exit()
