# Profile

Official documentation of [Meanwise Profile app](https://github.com/meanwise-eng/meanwise-server/tree/master/userprofile). 



#### 1. Profession Call:

* **Request URL:**

  `GET` `/api/v4/profession/`


* **Logic:** `Authentication Required`
  
    List all the professions. Authorization token will be required in the request header while sending a request to the URL.


* **Response:**

```javascript
{
  "count": 2,
    "next": null,
    "previous": null,
    "results":[
      {
          "id": 1,
        "text": "IT",
            "slug": "IT",
            "created_on": "2016-09-15T12:13:26.916938Z",
            "last_updated": "2016-09-15T12:13:26.916964Z",
            "searchable": true
        },
        {
          "id": 2,
            "text": "athlete",
            "slug": "athlete",
            "created_on": "2016-09-15T12:13:44.737235Z",
            "last_updated": "2016-09-15T12:13:44.737299Z",
            "searchable": true
        }
    ]
}
  
```


<br/>

#### 2. Skill call:

* **Request URL:**

  `GET` `/api/v4/skill/`
    

* **Logic:** `Authentication Required`
  
    List all the skills. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response**

```javascript
{
  "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
          "id": 1,
        "text": "python",
      "lower": "python",
            "slug": "python",
            "created_on": "2016-09-15T12:13:54.964201Z",
            "last_updated": "2016-09-15T12:13:54.964201Z",
            "searchable": true
    },    
        {   
          "id": 2,
      "text": "django",
            "lower": "django",
            "slug": "django",
            "created_on": "2016-09-15T12:14:14.290444Z",
            "last_updated": "2016-09-15T12:14:14.290471Z",
            "searchable": true
        }
   ]
}
```

<br/>

#### 3. Interest call:

* **Request URL:**

  `GET` `/api/v4/skills/` 

* **Logic:** `Authentication Required`
  
    List all the interests. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response**

```javascript
{
  "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
          "id": 1,
        "name": "sports",
            "slug": "sports",
            "description": "sports",
            "created_on": "2016-09-15T12:11:06.377205Z",
            "modified_on":"2016-09-15T12:11:06.377234Z",
      "published": false,
            "cover_photo": "https://squelo.com/media/interest_photos/IMG_20140525_164408761.jpg",
            "color_code": "asda"
        },  
        {
          "id": 2,
            "name": "music",
            "slug": "music",
            "description": "music",
            "created_on": "2016-09-15T12:12:18.297699Z",
      "modified_on": "2016-09-15T12:12:18.297726Z",
            "published": false,
            "cover_photo": "https://squelo.com/media/interest_photos/IMG_20140218_215136954.jpg",
            "color_code": "wrw"
        }
    ]
}
```

<br/>

#### 4. Userprofile:

* **Request URL:**
  
    `GET` `/api/v4/user/userprofile/`
    
* **Logic:** `Authentication Required`

  List the profile info of the user. Authorization token will be required in the request header while sending a request to the URL.
    
* **Response:**

``` javascript
{
  "count": 1,
    "next": null,
    "previous": null,
    "results":[
      {
        "id": 1,
          "facebook_token": "",
            "username": "testuser1",
            "first_name": "tfname1",
            "middle_name": "tmidname1",
            "last_name": "tlname1",
            "city": "bangalore",
            "profile_photo": "http://127.0.0.1:49100/http:/127.0.0.1:49100/media/profile_photos/IMG_20140321_104523179.jpg",
            "cover_photo": "http://127.0.0.1:49100/http:/127.0.0.1:49100/media/cover_photos/IMG_20140329_135903539.jpg",
      "bio": "Test bio",
            "created_on": "2016-09-15T12:17:13.786931Z",
            "last_updated": "2016-09-15T12:17:13.786953Z",
            "user": 2,
            "profession": 1,
            "skills": [1,2],
            "interests": [1,2]
        }
   ]
}
```