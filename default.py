#!/usr/bin/python
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, urllib, re, json, sys, os
from BeautifulSoup import BeautifulStoneSoup
from elementtree import ElementTree

__plugin__ = "SnagFilms"
__author__ = 'newatv2user <put email address here>'
__url__ = 'http://code.google.com/p/plugin/' # Don't know what to put here. Change as needed.
__date__ = '12-03-2011'
__version__ = '0.0.5'
__settings__ = xbmcaddon.Addon(id='plugin.video.snagfilms')

programs_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'programs.png')
topics_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'topics.png')
search_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'search.png')
next_thumb = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'next.png')

#modes
SF_MODE_CATEGORIES = 1
SF_MODE_SEARCH = 2
SF_MODE_LIST = 3
SF_MODE_LIST_NEW = 30
SF_MODE_LIST_MOST_LIKED = 31
SF_MODE_PLAY = 4
SF_DO_NOTHING = 5

#number of streams per page
ITEMS_PER_PAGE = 25

#####################################################
# List all global variable here
#####################################################
# Global Variables
_API_URL_ = 'http://api.snagfilms.com'
_API_VER_ = 'v1'
_CAT_XML_ = 'categories.xml'
_FILMS_ = 'films.xml'
_FILM_ = 'film.xml'
_DYN_LEAD_ = 'dynamicLead.xml'
_ANDROID_ = 'android'
_SWF_URL_ = 'http://www.snagfilms.com/assets/media-player/swf/MediaPlayer.swf'
_JSON_URL_ = 'http://www.snagfilms.com/api/assets.jsp?id='
	
# Is this being used? Delete if not
def clean(string):
	ulist = [('&amp;', '&'), ('&quot;', '"'), ('&#39;', '\''), ('\n', ''), ('\r', ''), ('\t', ''), ('</p>', ''), ('<br />', ' '), ('<b>', ''), ('</b>', ''), ('<p>', ''), ('<div>', ''), ('</div>', '')]
	for search, replace in ulist:
		string = string.replace(search, replace)
	return string

# This is the main directory when you first load the addon.
def build_main_directory():
	# set content type so library shows more views and info
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	# Top Title
	top = [
		(__settings__.getLocalizedString(30010), '', str(SF_DO_NOTHING))
		]
	for name, thumbnailImage, mode in top:
		addDir(name, '', mode, thumbnailImage, True)
	# Get featured contents
	build_dynamic_lead(True)
	# Static Links for Categories and Search
	main = [
		(__settings__.getLocalizedString(30001), topics_thumb, str(SF_MODE_CATEGORIES)),
		(__settings__.getLocalizedString(30003), search_thumb, str(SF_MODE_SEARCH))
		]
	for name, thumbnailImage, mode in main:
		addDir(name, '', mode, thumbnailImage, True)

	# End of Directory
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	## Set Default View Mode. This might break with different skins. But who cares?
	#xbmc.executebuiltin("Container.SetViewMode(503)")
	SetViewMode()
	#print 'Debug Msg: build_main_directory'
	
# Also called "Featured"
def build_dynamic_lead(mainS=False):
	DLUrl = buildDynamicLeadUrl()
	#if mainS == False:
	#	parseAndAddDynamicLeadTree(DLUrl)
	#else:
	parseAndAddDynamicLeadTree(DLUrl, mainS)
	#print 'Debug Msg: build_dynamic_lead'

# List the available Categories
def build_categories_directory():
	# Static categories
	staticCats = [
		(__settings__.getLocalizedString(30011), '', str(SF_MODE_LIST_NEW)),
		(__settings__.getLocalizedString(30012), '', str(SF_MODE_LIST_MOST_LIKED))
		]
	for name, thumbnailImage, mode in staticCats:
		addDir(name, '', mode, thumbnailImage, True)
	url = _API_URL_ + '/' + _API_VER_ + '/' + _CAT_XML_ + '?d=' + _ANDROID_
	categories = urllib2.urlopen(urllib2.Request(url))
	content = categories.read()
	categories.close()
	soupedCategories = BeautifulStoneSoup(content)
	for categoryI in soupedCategories.findAll('category'):
		catID = categoryI.find('id').string
		Title = categoryI.find('title').string
		addDir(Title, catID, SF_MODE_LIST, '', True)
	# End of Directory
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

	#print 'Done adding categories!'

# List Items of Category etc - Modify it to Index or sth like that				
def ListItems(category, offset):
	# set content type so library shows more views and info
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	if offset == None:
		offset = '0'
	caturl = buildCategoryUrl(category, offset)
	parseAndAddFilmsTree(caturl)
	# End of Directory
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	## Set Default View Mode. This might break with different skins. But who cares?
	#xbmc.executebuiltin("Container.SetViewMode(503)")
	SetViewMode()
	#print 'Debug Msg: ListItems'

#List New Items
def ListNewItems(offset):
	# set content type so library shows more views and info
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	# Get the URL first
	sort_type = 'newest'
	if offset == None:
		offset = '0'
	url = buildUrlForNewAndMostLiked(sort_type, offset)
	#print url
	parseAndAddFilmsTree(url)
	# End of Directory
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	## Set Default View Mode. This might break with different skins. But who cares?
	#xbmc.executebuiltin("Container.SetViewMode(503)")
	SetViewMode()
	
#List Most Liked
def ListMostLiked(offset):
	# set content type so library shows more views and info
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	# Get the URL first
	sort_type = 'liked'
	if offset == None:
		offset = '0'
	url = buildUrlForNewAndMostLiked(sort_type, offset)
	#print url
	parseAndAddFilmsTree(url)
	# End of Directory
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	## Set Default View Mode. This might break with different skins. But who cares?
	#xbmc.executebuiltin("Container.SetViewMode(503)")
	SetViewMode()
	
# Gets the parameters passed to the addon
def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params) - 1] == '/'):
			params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]					
	return param

# Add directory - Make this usable
def addDir(name, url, mode, iconimage, IsFolder=False, metainfo=False, offset=False, plot=False, year=False, duration=False, mpaa=False):
	meta = metainfo

	###  addDir with context menus and meta support  ###

	#encode url and name, so they can pass through the sys.argv[0] related strings
	# Handle utf-8 unicode encodings.
	sysname = urllib.quote_plus(name.encode('utf-8'))
	sysurl = urllib.quote_plus(url)
	sysimage = urllib.quote_plus(iconimage)

	#get nice unicode name text.
	#name has to pass through lots of weird operations earlier in the script,
	#so it should only be unicodified just before it is displayed.
	name = clean(name)

	u = sys.argv[0] + "?url=" + sysurl + "&mode=" + str(mode) + "&name=" + sysname + "&image=" + sysimage
	if offset is not False:
		u += '&offset=' + offset
	#ok = True

	#handle adding meta
	if meta == False:
		liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
		liz.setInfo(type="Video", infoLabels={"title": name})

	if meta is not False:    
		liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)

		infoLabels = {}
		if duration is not False:
			infoLabels['duration'] = duration
		if mpaa is not False:
			infoLabels['mpaa'] = mpaa
		if plot is not False:
			infoLabels['plot'] = plot
		if name is not False:
			infoLabels['title'] = name
		if year is not False:
			infoLabels['premiered'] = year

		liz.setInfo(type="Video", infoLabels=infoLabels)
		
	########
	#handle adding context menus
	contextMenuItems = []

	#if directory is an episode list or movie
	if mode == SF_MODE_PLAY:
		contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))

	if contextMenuItems:
		liz.addContextMenuItems(contextMenuItems, replaceItems=False)
	#########

	#Do some crucial stuff
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=IsFolder)
	return ok

		
# Build the api url for given CategoryID
def buildCategoryUrl(categoryID, offset):
	#print categoryID
	fCategoryID = categoryID.replace('-', '%2D')
	url = _API_URL_ + '/' + _API_VER_ + '/' + _FILMS_ + '?0=' + _ANDROID_ + '&1=' + fCategoryID + '&2=' + str(ITEMS_PER_PAGE) + '&4=' + offset + '&category%5Fid=' + fCategoryID + '&limit=' + str(ITEMS_PER_PAGE) + '&offset=' + offset + '&d=' + _ANDROID_
	#print url
	return url

def buildUrlForNewAndMostLiked(sort_type, offset):
	url = _API_URL_ + '/' + _API_VER_ + '/' + _FILMS_ + '?0=' + _ANDROID_ + '&2=' + str(ITEMS_PER_PAGE) + '&3=' + sort_type + '&4=' + offset + '&limit=' + str(ITEMS_PER_PAGE) + '&sort%5Ftype=' + sort_type + '&offset=' + offset + '&d=' + _ANDROID_
	return url
	
# Build search url
def buildSearchUrl(query):
	queryF1 = query.replace('-', '%2D')
	queryF2 = queryF1.replace(' ', '%20')
	url = _API_URL_ + '/' + _API_VER_ + '/' + _FILMS_ + '?d=' + _ANDROID_ + '&limit=' + str(ITEMS_PER_PAGE) + '&query=' + queryF2
	#print url
	return url

# URL for Featured	
def buildDynamicLeadUrl():
	url = _API_URL_ + '/' + _API_VER_ + '/' + _DYN_LEAD_ + '?0=' + _ANDROID_ + '&d=' + _ANDROID_
	#print url
	return url
	
# Build the film url for given FimlID
def buildFilmUrl(FilmID):
	#print FilmID
	fFilmID = FilmID.replace('-', '%2D')
	url = _API_URL_ + '/' + _API_VER_ + '/' + _FILM_ + '?0=' + _ANDROID_ + '&1=' + fFilmID + '&film%5Fid=' + fFilmID + '&d=' + _ANDROID_
	#print url
	return url
	
# Build the JSON url for given FimlID
def buildFilmUrlJSON(FilmID):
	#print FilmID
	#fFilmID = FilmID.replace('-', '%2D')
	url = _JSON_URL_ + FilmID
	#print url
	return url

# Build keyboard for search
def build_search_keyboard():
	keyboard = xbmc.Keyboard('', __settings__.getLocalizedString(30003))
	keyboard.doModal()
	if (keyboard.isConfirmed() == False):
		return
	search_string = keyboard.getText().replace(' ', '%20')
	if len(search_string) == 0:
		return
	build_search_directory(search_string)
	
# Build Search directory
def build_search_directory(query):
	# set content type so library shows more views and info
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	
	SearchUrl = buildSearchUrl(query)
	parseAndAddFilmsTree(SearchUrl)
	# End of Directory
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
	SetViewMode()

	
# Parse and add items from DynamicLead
def parseAndAddDynamicLeadTree(FixedURL, mainS=False):
	DLConn = urllib2.urlopen(urllib2.Request(FixedURL))
	MTreeS = DLConn.read()
	DLConn.close()
	MTree = ElementTree.fromstring(MTreeS)
	Slides = MTree.findall('slides')
	DLSlides = Slides[0].findall('dynamicLeadSlide')
	for DLSlide in list(DLSlides):
		Film = DLSlide.findall('film')[0]
		FilmID = Film.find('id').text
		Title = Film.find('title').text
		if mainS == True:
			Title = u'\u2022 ' + Title
		Plot = Film.find('logline').text
		Year = Film.find('year').text
		Minutes = Film.find('duration_minutes').text
		Seconds = Film.find('duration_seconds').text
		Duration = GetFormattedTime(Minutes) + ':' + Seconds
		Images = Film.find('images')
		if Images is not None:
			Image = Images.find('image')
			strImage = ElementTree.tostring(Image)
			ImageSrc = re.compile('<image height="317" src="(.+?)" type="android_poster" width="214" />').findall(strImage)[0]
		else:
			ImageSrc = ''
		MPAA = Film.find('rating').text
		addDir(Title, FilmID, SF_MODE_PLAY, ImageSrc, False, True, False, Plot, Year, Duration, MPAA)

	
# Parse and add items from Films Tree
def parseAndAddFilmsTree(FixedURL):
	DLConn = urllib2.urlopen(urllib2.Request(FixedURL))
	MTreeS = DLConn.read()
	DLConn.close()
	MTree = ElementTree.fromstring(MTreeS)
	NextOffsetSafe = MTree.find('next_offset')
	if NextOffsetSafe != None:
		NextOffset = NextOffsetSafe.text
	PageIndex = MTree.find('page_index').text
	PageTotal = MTree.find('page_total').text
	Films = MTree.findall('film')
	for Film in list(Films):
		FilmID = Film.find('id').text
		Title = Film.find('title').text
		Plot = Film.find('logline').text
		Year = Film.find('year').text
		Images = Film.find('images')
		Image = Images.find('image')
		strImage = ElementTree.tostring(Image)
		ImageSrc = re.compile('<image height="317" src="(.+?)" type="android_poster" width="214" />').findall(strImage)[0]
		Minutes = Film.find('duration_minutes').text
		Seconds = Film.find('duration_seconds').text
		Duration = GetFormattedTime(Minutes) + ':' + Seconds
		MPAA = Film.find('parental_rating').text
		addDir(Title, FilmID, SF_MODE_PLAY, ImageSrc, False, True, False, Plot, Year, Duration, MPAA)
	#print 'PageIndex: ' + PageIndex +  ' PageTotal: ' + PageTotal + ' NextOffset: ' + NextOffset
	if PageIndex != PageTotal and NextOffset != None:
		if mode == SF_MODE_LIST:
			addDir(__settings__.getLocalizedString(30013), url, mode, next_thumb, True, False, NextOffset)
		else:
			addDir(__settings__.getLocalizedString(30013), '', mode, next_thumb, True, False, NextOffset)


# Set View Mode selected in the setting
def SetViewMode():
	try:
		# if (xbmc.getSkinDir() == "skin.confluence"):
		if __settings__.getSetting('view_mode') == "1": # List
			xbmc.executebuiltin('Container.SetViewMode(502)')
		if __settings__.getSetting('view_mode') == "2": # Big List
			xbmc.executebuiltin('Container.SetViewMode(51)')
		if __settings__.getSetting('view_mode') == "3": # Thumbnails
			xbmc.executebuiltin('Container.SetViewMode(500)')
		if __settings__.getSetting('view_mode') == "4": # Poster Wrap
			xbmc.executebuiltin('Container.SetViewMode(501)')
		if __settings__.getSetting('view_mode') == "5": # Fanart
			xbmc.executebuiltin('Container.SetViewMode(508)')
		if __settings__.getSetting('view_mode') == "6":  # Media info
			xbmc.executebuiltin('Container.SetViewMode(504)')
		if __settings__.getSetting('view_mode') == "7": # Media info 2
			xbmc.executebuiltin('Container.SetViewMode(503)')
		
		if __settings__.getSetting('view_mode') == "0": # Default Media Info for Quartz
            		xbmc.executebuiltin('Container.SetViewMode(52)')
	except:
		print "SetViewMode Failed: " + __settings__.getSetting('view_mode')
		print "Skin: "+xbmc.getSkinDir()		

# Get Time in HH:MM format
def GetFormattedTime(Min):
	Minutes = int(Min)
	Quotient = Minutes / 60
	Remainder = Minutes % 60
	HHMM = str(Quotient) + ':' + str(Remainder)
	return HHMM	

	
# Get rtmp link (highest bitrate)
# To-do allow selection of different bitrates
def getRTMPLink(FilmInfoUrl):
	#print FilmInfoUrl
	req = urllib2.Request(FilmInfoUrl)
	response = urllib2.urlopen(req)
	FilmInfo = response.read()
	response.close()
	soupedFilmInfo = BeautifulStoneSoup(FilmInfo)
	RenditionsT = soupedFilmInfo.find('renditions')
	RenditionsET = ElementTree.fromstring(str(RenditionsT))
	prevURI = ''
	prevBR = 0
	for Rendition in list(RenditionsET):
		URI = Rendition.find('url')
		thisURI = URI.text
		BR = Rendition.find('bitrate')
		thisBR = int(BR.text)
		if thisBR > prevBR:
			prevURI = thisURI
			prevBR = thisBR
	return prevURI
	
# Get rtmp link (highest bitrate)
# To-do allow selection of different bitrates
# Above rtmp link don't play
def getRTMPLinkV2(FilmInfoUrl):
	#print FilmInfoUrl
	req = urllib2.Request(FilmInfoUrl)
	response = urllib2.urlopen(req)
	FilmInfo = response.read()
	response.close()
	snagJson = json.loads(FilmInfo)
	resultJson = snagJson['result']
	rtmp = resultJson['host']
	streams = resultJson['video']
	prevURI = ''
	prevBR = 0
	for stream in list(streams):
		thisURI = stream['streamName']
		thisBR = int(stream['bitrate'])
		if thisBR > prevBR:
			prevURI = thisURI
			prevBR = thisBR
	return rtmp + ' playpath=' + prevURI
	
# Play the movie
def PlayItem(item, title, image):
	#print 'PlayItem : item - ' + item
	#print 'PlayItem : title - ' + str(title)
	#print 'PlayItem : image - ' + str(image)
	#FilmInfoUrl = buildFilmUrl(item)
	FilmInfoUrl = buildFilmUrlJSON(item)
	RTMPLink = getRTMPLinkV2(FilmInfoUrl)
	vid = xbmcgui.ListItem(label=title, iconImage="DefaultVideo.png", thumbnailImage=image)
	vid.setInfo(type="Video", infoLabels={ "Title": title })
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(RTMPLink, vid)


# Addon variables
params = get_params()
mode = None
name = None
url = None
'''thumb = None
plot = None
item = None
title = None'''
image = None
#category = None
offset = None

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
try:
	image = urllib.unquote_plus(params["image"])
except:
	pass
try:
	offset = urllib.unquote_plus(params["offset"])
except:
	pass
	
if mode == None:
	print __plugin__ + ' ' + __version__ + ' ' + __date__
	build_main_directory()
elif mode == SF_DO_NOTHING:
	print 'Doing Nothing'
elif mode == SF_MODE_CATEGORIES:
	build_categories_directory()
elif mode == SF_MODE_SEARCH:	
	build_search_keyboard()
elif mode == SF_MODE_LIST:
	ListItems(url, offset)
elif mode == SF_MODE_LIST_NEW:
	ListNewItems(offset)
elif mode == SF_MODE_LIST_MOST_LIKED:
	ListMostLiked(offset)
elif mode == SF_MODE_PLAY:
	PlayItem(url, name, image)
