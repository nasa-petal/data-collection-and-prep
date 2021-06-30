import pyautogui, re, time, os
from bs4 import BeautifulSoup

def get_doi_using_pyautogui(url):
	time.sleep(2)  # the time it takes to open up Chrome
	
	# TODO - update all .pdf urls in the AirTable with their equivalent HTML webpage
	if '.pdf' in url:
		print('PDF file, no DOI found for now.')
		return ''

	# file_name = url.split('/')[-1].split('?')[0]
		# Originally, I parsed the url to obtain a name for the to-be-saved HTML file, like so:
		# Ex, https://www.jstor.org/stable/24874508?seq=1 => 24874508.
	# but, with so many urls coming from different journals, this parsing method became problematic, since
		# there were file names with bad characters in them (ex ,./:;'),and many of the file names were reused.
	# the timestamp method is better because file names are more organized and definitely won't be reused.
	file_name = round(time.time())  # current time in seconds

	# open a new tab, enter the url, and wait for the site to load
	pyautogui.hotkey('command', 't')
	pyautogui.typewrite(f'{url}\n')
	time.sleep(5)

	path = os.getcwd() # the path to the directory which get_doi_using_pyautogui.py is in
	pyautogui.hotkey('command', 's')  # bring up the pop-up for saving files
	time.sleep(2)  # wait for the pop-up to load
	pyautogui.typewrite(f'{path}/{file_name}.html\n') # this '\n' is for confirming the path of the to-be-saved file
	time.sleep(2)
	pyautogui.typewrite('\n') # this '\n' is for confirming the file download
	time.sleep(10) # wait for the file to download

	# close the tab since the loaded website is now saved
	pyautogui.hotkey('command', 'w')

	# open the file which was just saved and give BeautifulSoup its HTML
	html = open(f'{path}/{file_name}.html', "r").read()
	soup = BeautifulSoup(html, 'html.parser')
	
	doi = ''  # default doi value if nothing is found
	
	# search the HTML for DOIs displayed as hrefs
	# TODO - write test code for this, since it is risky to just take the first DOI that is found and assume it's valid
	for a in soup.find_all('a', href=True):
		link = a['href']

		# must include 'https://www.' because some hrefs may contain just 'doi' in them as a false alarm
		if 'https://www.doi.org/' in link:
			doi = link.split('https://www.doi.org/')[1]
			break

	# search the HTML for DOIs displayed as strings
	# TODO - write some test code for this, because some strings may obey the regex but be an invalid DOI
	if len(doi) == 0:
		print('Pulling from text')
		# need to use a more sophisticated DOI regex
		#   https://www.crossref.org/blog/dois-and-matching-regular-expressions/
		#   https://www.regextester.com/93795

		# TODO - determine differences between Python 2 and 3 for regex
		# TODO - update soup() call to find_all, which is more explicit
		# TODO - read documentation to see what happens if nothing is found with find_all()
		doi = soup(text=re.compile("^10.\d{4,9}/[-._;()/:A-Za-z0-9]+$"))[0].strip()

		# removing all characters before first number in DOI
		# TODO - split the DOI using plain Python rather than regex.
		# TODO -  read documentation to see what happens if nothing is found with re.search()
		doi = re.search('[0-9].*', doi)[0]

	return doi

########################################################################################################################
# to use this function:
bad_urls = open('bad_urls.txt', 'r').readlines()  # list of urls that have stubborn DOIs for scraping

count = 0
for url in bad_urls:
	count += 1
	doi = get_doi_using_pyautogui(url)
	
	# for debugging purposes
	print(f'Line {count}: {url.strip()}')
	print(f'DOI: {doi}\n')