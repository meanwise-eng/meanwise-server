# Channels

Documentation for Channels app API endpoints. 

## URL

#### 1. `/channel/create/` `POST`


* **Parameters:**
  - channel_name (unique)
  - description
  - channel_type
  - tags (Array)
  - coverphoto
  - profilepic
  - slugfield (automatically created)
  - created_on
  

* **Logic:** `Authentication Required`

	Create a channel with all the required fields and returns success status if successfully created. 

* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
		"success": "Successfully created."
	}	
}
```

* **Request Sent:**

```json
{
	"channel_name": "xyz",
    "description": "some-text",
    "channel_type": "type of channel",
    "tags": ["#tag1", "#tag2"],
    "coverphoto": "abc.jpeg",
    "profilepic": "xyz.jpeg",
    "created_on": "date",
    "slug_field": "<channel_name>"
}
```

<br/>

#### 2. `/<channel_slug>/` `GET`


* **Logic:** `Authentication Required`

	List channel details if channel exists. Also list all the posts posted on the channel or by the channel where posts are array of objects.

* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
		"channel_name": "xyz",
        "description": "some-text",
        "channel_type": "type of channel",
        "tags": ["#tag1", "#tag2"],
        "coverphoto": "abc.jpeg",
        "profilepic": "xyz.jpeg",
        "posts": {
        	"data": [
                {
                   "id": "1015012",
                   "url": "post_url",
                },
                {
                   "id": "1090012",
                   "url": "post_url",
                },
             ],
        },
        "created_on": "date",
        "slug_field": "<channel_name>"
	}	
}
```

* **Overview:**

![alt text](https://github.com/meanwise-eng/meanwise-server/blob/master/docs/Chnnels.png "Channels")

<br/>

#### 3. `/<channel_name>/post/` `POST`


* **Parameters:**
  - publisher (automatically created)
  - image / video (if any)
  - posttext (can also have line breaks)
  - action - like / comment /share
  - published_date
  - unique url / slug for post (automatically created)
  

* **Logic:** `Authentication Required`

	Create a post on a channel. 

* **Request Sent:**

```json
{
    "published_by": "Abc",
    "image": "abc.jpeg",
    "post-text": "Hey",
    "comments": {
      "data": [
        {
          "id": "1015012",
          "from": {
            "name": "Grover",
            "id": "614130500"
          },
          "message": "some messge",
          "created_time": "time"
        },
        {
          "id": "101501",
          "from": {
            "name": "Some-name",
            "id": "688036079"
          },
          "message": "some message",
          "created_time": "time"
        }
      ]
    },
    "likes": {
      "data": [
        {
          "id": "1015012",
          "from": {
            "name": "Grover",
            "id": "614130500"
            }
        },
      ]
    },
    "share": {
      "data": [
        {
          "id": "1329332",
          "from": {
            "name": "Grover",
            "id": "1203292",
            "url": "post_url"
          }
      	}
      ]
    },
    "published_date": "time",
    "slug_field": "<post_publisher/post_id>",
    "response": {
    	"success": "Successfully posted"
    }
}
```

<br/>

#### 4. `/<channel_name>/post/<slug_field>` `GET`
 

* **Logic:** `Authentication Required`

	Show a particular post on a channel. 

* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
      	"published_by": "Abc",
      	"image": "abc.jpeg",
      	"post-text": "Hey",
      	"comments": {
            "data": [
                {
                   "id": "1015012",
                   "from": {
                      "name": "Grover",
                      "id": "614130500"
                   },
                   "message": "some messge",
                   "created_time": "time"
                },
                {
                   "id": "101501",
                   "from": {
                      "name": "Some-name",
                      "id": "688036079"
                   },
                   "message": "some message",
                   "created_time": "time"
                }
            ],
       	},
       	"likes": {
        	"data": [
                {
                   "id": "1015012",
                   "from": {
                      "name": "Grover",
                      "id": "614130500"
                	}
                },
            ]
        },
        "share": {
        	"data": [
            	{
                	"id": "1329332",
                    "from": {
                    	"name": "Grover",
                        "id": "1203292",
                        "url": "post_url"
                    }
                },
            ]
        },
        "published_date": "time",
        "slug_field": "<post_publisher/post_id>",
     }
}
```

<br/>


#### 5. `/<channel_name>/subscribe/` `POST`


* **Parameters:**
  - user_id
  - follow (boolean)
  

* **Logic:** `Authentication Required`

	Subscribe to a channel.


* **Request Sent:**

```json
{
    "user_id": "123243243249880",
    "follow": "True",
}
```

* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
		"success": "Successfully subscribed."
	}	
}
```

<br/>


#### 6. `/<channel_name>/unsubscribe` `POST`


* **Parameters:**
  - user_id
  - follow (boolean)
  

* **Logic:** `Authentication Required`

	Unsubscribe a channel

* **Request Sent:**

```json
{
    "user_id": "123243243249880",
    "follow": "False",
}
```

* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
		"success": "Successfully Unsubscribed."
	}	
}
```

<br/>


#### 6. `/<channel_name>/list/` `GET`

* **Logic:** `Authentication Required`

	List all the users subscribed to a channel

* **Response:**

```json
{
	"status": "HTTP 200 OK",
	"response": {
		"user": {
        	"data": [
            	{
                	"user_id": "12912390218308",
                    "can_directmessage": "False",
                    "connect": "False",
                },
                {
                	"user_id": "12912390218308",
                    "can_directmessage": "False",
                    "connect": "False",
                },
            ]
        },
        "success": "Succesfully shown the list of users."
	}	
}
```

<br/>
