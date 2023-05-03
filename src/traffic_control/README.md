# Traffic Control
Traffic Control is a web application that allows you to control your linux device. It is written in Python and uses the Django framework. It is currently in development and is not ready for production use.

## Features
* Policy based firewall
* Policy based routing
* Policy based QoS

## Requirements
* TC linux module
* pyroute2

## Documentation
TODO


## Routes


### /
Methods: GET
#### GET:
Return: render index.html

--------------

### /api/1.0/policy
Methods: GET, POST
#### GET: 
List all policies
(name and description)

params: 
* `page` - page number
* `per_page` - number of policies per page
Return: JSON of all policies
#### POST: 
Create a new policy

Body:
* `name` - name of policy
* `description` - description of policy
* `config` - config of policy

Return: JSON of new policy

--------------

### /api/1.0/policy/:id
Methods: GET, PATCH, PUT, DELETE
#### GET:
Get a policy by id

Return: JSON of policy

#### PUT:
Update a policy by id

Body:
* `name` - name of policy 
* `description` - description of policy
* `config` - config of policy
* `startup` - run on startup?
* `enabled` - enable policy?

One and only oneof the above fields must be present

Return: JSON of updated policy

#### PUT:
Update a policy by id

Body:
* `name` - name of policy (required)
* `description` - description of policy (required)
* `config` - config of policy (required)
* `startup` - run on startup? (required)
* `enabled` - enable policy? (required)

At least one of the above fields must be present

Return: JSON of updated policy

#### DELETE:
Delete a policy by id

Return: JSON of deleted policy
