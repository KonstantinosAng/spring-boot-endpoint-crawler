# Spring Boot Endpoint Crawler

<br />

## **This repo is not completed yet, thus bugs are real 😁**

<br />

A simple python script to find all endpoints in a spring boot microservice in 100 lines.

## Installation

The only requirement is python, tested with python 3.8.5

## Usage

For searching the files in the scripts directory.

```bash
python search.py
```

For searching the files in a directory

```bash
python search.py /path/you/want/to/search
```

The scripts does not alter the files as it opens them in read only mode.

## Example

An example output of a microservice endpoints

```bash
*************************
|> File: FileName.java <|
*************************
[BASE]:  "/api/v1/path/"
-- [POST]:  "/api/v1/path/endpoint-1/"
---- [BODY]:  Map<String, String> param1
-- [POST]:  "/api/v1/path/endpoint-2/"
---- [PARAM]:  (required = true) Map<String, String> param1
---- [BODY]:  Map<String, String> bodyParam1
-- [GET]:  "/api/v1/path/endpoint-3/{id}/{slug}"
-- [GET]:  "/api/v1/path/endpoint-4/{id}/{slug}/details"
-- [PATCH]:  "/api/v1/path/endpoint-5/{id}/{slug}/update"
-- [DELETE]:  "/api/v1/path/endpoint-6/{id}/{slug}/delete"
```
