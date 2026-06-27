---
name: crawler-config-batch
description: Analyze a website and generate multiple crawler DSL configurations.
---


# Crawler Config Batch Skill


## Purpose


Generate multiple crawler configurations from one website.



## Workflow


Website

↓

Discover categories

↓

Analyze APIs

↓

Generate DSL

↓

Save files



---

# Category Discovery


Search:


- category
- type
- code
- menu
- announcement


Extract:


- name

- code

- url



---

# API Analysis


Priority:


1. REST API

2. JSON embedded

3. HTML


Do not prefer browser automation.



---

# Configuration Rules


Always generate:

```json
{
"entranceUrl":"",
"list":{},
"detail":{},
"pagination":{},
"fields":[]
}