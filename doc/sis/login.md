## Login form
url: `http://www.sexinsex.net/bbs/index.php`
form selector: `#loginform`
input field selector: `#loginform [name]`
user name input name: `username`
password input name: `password`

## Login success page

It's a 200 page.

We can test using:
```javascript
document.querySelector(".box.message").textContent.indexOf("xxx user name") >= 0
```