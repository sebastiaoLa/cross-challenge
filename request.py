import json
import requests
import redis
from datetime import datetime

CACHE_MAX_AGE = 60 # maximum amount of time in seconds a resource is fresh

r = redis.Redis(host='localhost', port=6379, db=0)

def order_params(params):
    # Sort params by key
    # This code is here to avoid ?key1=value1&key2=value2 and ?key2=value2&key1=value1 from been two entries on cache
    params_list = [(i, params[i]) for i in params]
    params_list.sort(key=lambda x: x[0])
    return params_list

def retrieve_cache_domain(url):
    #Remove protocol from url and get domain
    return url.split('://')[-1].split('/')[0]

def retrieve_cache_params(url, parameters):
    return {
        #Remove protocol from url and get everything that comes after the domain
        "path":url.split('://')[-1].split('/')[1:],
        "params":order_params(parameters) if parameters else None
    }

def invalidade_cache(url):
    #remove cache entry from redis database
    cache_domain = retrieve_cache_domain(url)
    r.delete(cache_domain)

def get(url, parameters=None):
    """ Fetches an URL and returns the response """
    cache_domain = retrieve_cache_domain(url)
    cache_params = retrieve_cache_params(url, parameters)
    #Check redis database for cached version
    cached = r.hget(cache_domain, json.dumps(cache_params))
    if cached:
        response = json.loads(cached)['response']
        #Check if version on database is still fresh enough
        if int(json.loads(cached)['timestamp'])+CACHE_MAX_AGE > int(datetime.now().strftime("%s")):
            return response

    response = requests.get(url, params=parameters).json()
    #Saves response on cache
    r.hset(cache_domain, json.dumps(cache_params), json.dumps({"timestamp":datetime.now().strftime("%s"), "response":response}))
    return response

def post(url, parameters=None, data=None):
    """ Post data to an URL and returns the response """
    invalidade_cache(url)
    return requests.post(url, params=parameters, data=data).json()


def put(url, parameters=None, data=None):
    """ Put data to an resource and returns the response """
    invalidade_cache(url)
    return requests.put(url, params=parameters, data=data).json()


def patch(url, parameters=None, data=None):
    """ Patches an resource and returns the response """
    invalidade_cache(url)
    return requests.patch(url, params=parameters, data=data).json()


def delete(url, parameters=None, data=None):
    """ Requests the deletion of an resource and returns the response """
    invalidade_cache(url)
    return requests.delete(url, params=parameters, data=data).json()

#Demo
t_0 = datetime.now()
print("Invalidating cache")
print(post("https://jsonplaceholder.typicode.com/posts/", data={'userId': 1, 'title': 'quis ut nam facilis et officia qui', 'body': ''}))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("First request")
print(get("https://jsonplaceholder.typicode.com/posts/2"))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Second request")
print(get("https://jsonplaceholder.typicode.com/posts/2"))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Third request")
print(get("https://jsonplaceholder.typicode.com/posts/2"))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Invalidating cache")
print(post("https://jsonplaceholder.typicode.com/posts/", data={'userId': 1, 'title': 'quis ut nam facilis et officia qui', 'completed': False}))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("First request")
print(get("https://jsonplaceholder.typicode.com/posts/2"))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Second request")
print(get("https://jsonplaceholder.typicode.com/posts/2"))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Third request")
print(get("https://jsonplaceholder.typicode.com/posts/2"))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Invalidating cache")
print(post("https://jsonplaceholder.typicode.com/posts/", data={'userId': 1, 'title': 'quis ut nam facilis et officia qui', 'completed': False}))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("First request with params")
print(get("https://jsonplaceholder.typicode.com/posts/", parameters={"userId":"1"}))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Second request with params")
print(get("https://jsonplaceholder.typicode.com/posts/", parameters={"userId":"1"}))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )

t_0 = datetime.now()
print("Third request with params")
print(get("https://jsonplaceholder.typicode.com/posts/", parameters={"userId":"1"}))
print(f"Took {(datetime.now() - t_0).microseconds/1000.0}ms\n" )
