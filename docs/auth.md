# Authentication

Official documentation for Meanwise - **[Authentication](https://github.com/meanwise-eng/meanwise-server/tree/master/custom_auth)**.

#### 1. For normal registration - Django way
* **Request URL:**

	`/api/v4/custom_auth/user/register/` `POST`


* **Parameters:**

Parameter | Type | Required Field | 
:------------: | :-------------: | :------------: | 
Username | String | ✓ 
 Email| String | ✓
 Password | String | ✓
 First Name | String | ✓
 Middle Name | String | ✕ 
 Last Name | String | ✕ 
 Profession | Professsion Object| ✓
 Skills | List Field | ✓
 Interests | List Field | ✓
 Invite code | String | ✓
 City | String | ✕
 Profile Phtoto | Image | ✕
 Cover Photo | Image | ✕
 Bio | String | ✕
 

* **Logic:**

	Handle Registering of user for normal django flow. Capture all user information at one go. For each user generate auth token and use the same to authorize further api calls.
	
* **Request:**

```json
{	
	"register":
    {
    	"username":"testuser3@test.com", 		 
    	"email":"testuser3@test.com",
    	"password":"testpassthree",
        "first_name":"testfname4", 
        "profession":1,
        "skills":[1,2],
        "interests":[1,2], 
        "invite_code":"REALPEOPLE"
    }
}
```


* **Response:**

```json
{
	"userprofile":10,
    "auth_token":"e73e7c1e402c36a920907c239c7ccd0b324fe18a",
    "user":15
}
```

<br/>

#### 2. Facebook Signup
* **Request URL:** 

	`/api/v4/custom_auth/user/register/` `POST`

* **Parameters:**

Parameter | Type | Required Field | 
:------------: | :-------------: | :------------: | 
Username | String | ✓ 
 Email| String | ✓
 Facebook Token | String | ✓
 Password | String | ✓
 First Name | String | ✓
 Middle Name | String | ✕ 
 Last Name | String | ✕ 
 Profession | Professsion Object| ✓
 Skills | List Field | ✓
 Interests | List Field | ✓
 Invite code | String | ✓
 City | String | ✕
 Profile Phtoto | Image | ✕
 Cover Photo | Image | ✕
 Bio | String | ✕
 

* **Logic:**
	
	Handle Registering of user for facebook flow. Capture all user information at one go. For each user generate auth token and use the same to authorize further api calls.
    
* **Request:** 

```json

{
	"register": {
    	"username":"testuser8@test.com", 
        "email":"testuser8@test.com",
        "facebook_token":"fbtokeneight",
        "first_name":"testfname8", 
        "profession":1,"skills":[1,2],
        "interests":[1,2]
    }
}
```
	
* **Response:**

```json
{	
	"auth_token":"63cd2dda1508e2bcfe15550b53930f7792598e84",
    "user":13,
    "userprofile":9
}
```

<br/>

#### 3. Retrieve auth token

* **Request URL:**

	`/api/v4/custom_auth/api-token-auth/` `POST`

* **Parameters:**

Parameter | Type | Required Field 
:------------: | :-------------: | :------------: 
Username | String | ✓ 
Password | String | ✓

* **Logic:**

	To retrieve user token given username and password.
    
* **Request:**

```json
{
	"username":"testuser5@test.com",
    "password":"testpassfive"
}
```
	
* **Response:**

```json
{
	"token":"93deff3e4c04e5f2ee1349035fd7637bb4df7aa0"
}
```

<br/>

#### 4. Verify Email.

* **Request URL:** 

	`/api/v4/custom_auth/user/verify/` `POST`

* **Parameters:**

Parameter | Type | Required Field 
:------------: | :-------------: | :------------: 
Email | String | ✓ 

* **Logic:**

	Check if the email exists or not.
    
* **Request:**

```json
{
	"email":"testuser5@test.com"
}
```

* **Response:**

```json
{
	"exists":"true"
}
```