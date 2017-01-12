# urlshorten
A super tiny url shortener with a simple API

## Running
urlshorten is a simple Flask app, so it can run anywhere you have python. 
I also made a Dockerfile and docker-compose.yml if you like containers.
Just run `docker-compose up` if you want to try that out.

## API

### POST /urls/
#### Parameters
- `url=https://example.com`: The long url you want to shorten
- `secret=false`: Secret urls are longer and hidden from the /urls overview

Returns a json blob that looks like this, where 's' the shortened url:
```json
{
  "status": 200,
  "message": "s"
}
```
#### Errors
- 400 'Use the argument \`url\`': You didn't supply the url argument
- 400 'Not a valid url': The url wasn't matched by the url regex
- 500 'Some error message': There was an internal error

### GET /urls/
#### Parameters
- `page=1`: The page for the result. (Pages are 25 urls long.)

Returns a list of shortened urls (excluding secret urls) that looks like this:
```json
{
  "status": 200,
  "message": {
    "s": "https://example.com"
  }
}
```
#### Errors
- 500 'Some error message': There was an internal error

### GET /urls/\<url_id\>
Returns a the long url for the url_id:
```json
{
  "status": 200,
  "message": "https://example.com"
}
```

#### Errors
- 404 'Not found': The requested url_id was not found
