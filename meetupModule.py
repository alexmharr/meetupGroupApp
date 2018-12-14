import urllib.request, urllib.error, urllib.parse, json
import plotly.plotly as py
from plotly.offline import plot
import plotly.graph_objs as go
import urllib, webbrowser, json
import jinja2


from auth import *
import os
import logging

#Signing into Plot.ly Service
py.sign_in('aharr', plot_api_key)

#Setting up the jinja environment
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


#Utility Functions
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None


# Defines the generic function that makes calls to the meetup API
# You can specify a method you would like to use plus any additional parameters
def meetREST(baseurl = 'https://api.meetup.com/',
             method = '2/categories',
             api_key = api_key,
             params={},
             format ='json'):
    #Setting the params
    params['fields'] = format
    params['key'] = api_key
    url = baseurl + method + "?" + urllib.parse.urlencode(params)
    return safeGet(url)


# Function allows you to find groups in your specified zip code.
# Can also limit how many entries you want
def findgroup(zip_code, radius=20):
    request = meetREST(method='find/groups',
                       params={'zip': zip_code, 'radius': radius}).read()
    dict = json.loads(request)
    return dict



class Group():
    """This class takes in a dictionary from findgroup() and pulls certain keys out
    and sets them as instance variables"""

    def __init__(self, group_dict):
        self.category_name = group_dict['category']['name']
        self.city = group_dict['city']
        self.country = group_dict['country']
        self.description = group_dict['description']
        if 'group_photo' in group_dict:
            self.group_photo = group_dict['group_photo']['photo_link']
        else:
            self.group_photo = None
        self.can_join = group_dict['join_mode']  # If people can join the group
        self.lat = group_dict['lat']
        self.lon = group_dict['lon']
        self.link = group_dict['link']  # Link to meetup page
        self.member_count = group_dict['members']
        self.group_name = group_dict['name']
        if 'next_event' in group_dict:
            self.next_event = group_dict['next_event']['name']  # another dictionary
        else:
            self.next_event = None

    def __str__(self):
        if len(self.description) > 100:
            self.description = self.description[0:100] + "..."

        return "Group Name: {}\nCategory: {}\nLocation: {}, " \
               "{}\nDescription: {}\nLink to Group: {}".format(self.group_name, self.category_name,
                                                               self.city, self.country, self.description,
                                                               self.link)

    def open_url(self):
        webbrowser.open(self.link)


def makeGroupObjects(list_of_groups):
    """Returns a list of groups objects
    Parameters:
        List of groups from findGroups
    Returns:
        list of Group Objects
    """

    group_list = [Group(x) for x in list_of_groups]
    return group_list

groups = makeGroupObjects(findgroup('95125', 20))


def getAttributes(datalist):
    """
    Returns a nested dictionary of select group object data
    for mapping using plot.ly

    :param datalist: list of groupobjects
    :return summary_dict: a dictionary of select info from each group object
    """
    summary_dict = {}
    for point in datalist:
        name = point.group_name
        lat = point.lat
        lon = point.lon
        category = point.category_name
        location = point.city + ", " + point.country
        link = point.link
        description = point.description
        if len(description) > 100:
            description = description[0:100] + "..."
        summary_dict[name] = {'coordinates': {'lat': lat, 'lon': lon},
                                 'info': {'category': category, 'location': location,
                                          'description': description,
                                          'link': link}}
    return summary_dict



def generateScatterObjects(groupInfo):
    """
    This function generates a list of scattermapbox objects that will be used to generate plots

    :param groupInfo: dict containing coordinates and other relevant info
    :return scatter_list: list of scattermapbox objects
    """

    scatter_list = list()

    for coord in groupInfo.keys():
        scatterplot = go.Scattermapbox(
            name=coord,
            lat=[groupInfo[coord]['coordinates']['lat']],
            lon=[groupInfo[coord]['coordinates']['lon']],
            mode='markers',
            marker=dict(
                symbol='circle',
                size=10,
            ),
            text=coord,
            hoverinfo='text',
        )
        scatter_list.append(scatterplot)

    return scatter_list


def generateGroupPlots(zip_code, radius=20):
    """
    This function generates the meetup plots based off of a certain zip code
    :param zip_code: zip_code of the user
    :param radius: how many meetups the user wants to view
    :return: a url of the plot
    """

    center_list = makeGroupObjects(findgroup(zip_code, radius))[0]  # For centering the map

    groupInfo = getAttributes(makeGroupObjects(findgroup(zip_code, radius)))
    data = generateScatterObjects(groupInfo)

    layout = go.Layout(
        title='Find Meetups',
        autosize=True,
        hovermode='closest',
        hoverlabel=dict(

        ),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        paper_bgcolor='#202020',
        mapbox=dict(
            style='dark',
            accesstoken=map_api_key,
            bearing=0,
            center=dict(
                lat=center_list.lat,
                lon=center_list.lon
            ),
            pitch=0,
            zoom=10
        )
    )
    context ={}
    fig = dict(data=data, layout=layout)
    url = plot(fig, auto_open=False, output_type='div')
    return url
    # url = plot(fig, filename='static/search.html', auto_open=False, show_link=False)
    # return url
