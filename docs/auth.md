## Authentication

For authentication we are using [Django allauth](https://django-allauth.readthedocs.io/en/latest/)  and [Django rest-auth](https://github.com/Tivix/django-rest-auth). 

#### URL
* **/user/register (POST)**
Parameters:
	- username (string)
	- email (string)
	- password1 (string)
	- password2 (string)
	- access token

	Logic : Create user with username/email , store the access token, generate auth 	token and send a verification email
	
	Response: 
```
{
	"status": "HTTP 200 OK",
	"response": {
		"access_token": "jabhjbsadfjbsadf231312",
		"username": "grover",
		"success": "Successfully signed up and an email has been sent to your email id "
	}	
}
```

* **/user/login/ (POST)**
Parameters:
	- username (string)
	- password (string)
	- email

	Logic:  Checks if the user exists or not if yes then update the auth token object to that user and redirects to the home view.
	
	Response:
```
{	
	"status": "HTTP 200 OK",
	"response": {
		"success": "Successfully loggin out."
	}
}
```

* **/user/logout/ (POST, GET)**
Parameters:
	- token

	Logic:  Calls Django logout method and delete the Token object assigned to the current User object. Accepts/Returns nothing.  
	
	Response:
```
{	
	"status": "HTTP 200 OK",
	"response": {
		"success": "Successfully logged out."
	}
}
```

* **/user/password/reset/ (POST)**
Parameters:
	- email

	Logic:  Calls Django Auth PasswordResetForm save method. Accepts the following POST parameters: email. Returns the success/fail message.

	Response:

```
{
	"status": "HTTP 200 OK",
	"response": {
		"success": "Password reset e-mail has been sent."
	}
}
```

* **/user/password/reset/confirm/ (POST)**
Parameters:
	- uid
	- token
	- new_password1
	- new_password2

	Logic: Password reset e-mail link is confirmed, therefore this resets the user's password. Accepts the following POST parameters , Django URL arguments and returns the success/fail message.

	Response: 
```
{
	"response": {
		"success": "Password has been reset with the new password."
	}
}
```

* ** /user/password/change/ (POST)**
Parameters:
	- new_password1
	- new_password2
	- old_password

	Logic: Calls Django Auth SetPasswordForm save method. Accepts the POST parameters and returns the success/fail message.

	Response:
```
{
	"response": {
		"success": "New password has been saved."
	}
}
```

* ** /user/ (GET)**
	Logic: Returns User's details in JSON format.
	Response:
```
{	
	"user": {
		"email": "abc@gmail.com",
		"username": "grover",
		...
		"date_joined": "some date"
	}
}
```

* **/user/ (PUT/PATCH)**
Parameters:
	- username
	- email
	- first_name
	- last_name

	Logic: Update user's details and return updated user details in JSON format.

	Response: 
```
{	
	"user": {
		"email": "abc@gmail.com",
		"username": "grover",
		...
		"date_joined": "some date"
	}
}
```
