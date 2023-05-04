# Traffic Control
Traffic Control allows you to control your linux device traffic. 
It is the first application in Linux to allow you to easily control your programs traffic.
Without the need to rerun or run the program as a specific user or in a specific container.


## Features
- Limit upload and download rate, burst, and latency control
    - Traffic Shaping
    - Traffic Policing

- Filters
    - Program
        - Cgroups
        - Program name
    - Match
        - IP address [src, dst]
        - Port [src, dst]
        - Protocol [tcp, udp]
    - Interface
        - Interface name
    



## Requirements
* Python 3.6+
* Systemd (optional for filter by program name)
* pyroute2
* TC linux module

## Documentation
TODO


## Routes


### /
Methods: GET
#### GET:
Return: render index.html

--------------

### /policy
Methods: GET, POST
#### GET: 
List all policies

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
* `enabled` - enable policy?
* `startup` - run on startup?

Return: JSON of new policy

--------------

### /policy/:id
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

--------------

## Additional Routes
These routes are used by the web interface.
for the most part they are the same as the above routes.
However they provide a simpler interface for the web frontend.

### /program_policy
Methods: GET, POST
#### GET: 
List all program policies
In simpler format than /policy

params: 
* `page` - page number
* `per_page` - number of policies per page
Return: JSON of all policies

#### POST: 
Create a new program policy

Body:
* `name` - name of policy
* `description` - description of policy
* `enabled` - enable policy?
* `startup` - run on startup?
* `programs` - list of programs to apply policy to
* `rate` - rate to limit program to
* `burst` - burst to limit program to
* `prio` - priority to limit program to

Return: JSON of new policy

--------------

### /program_policy/:id
Methods: GET, PATCH, PUT, DELETE
#### GET:
Get a program policy by id

Return: JSON of policy

#### PUT:
Update a policy by id

Body:
* `name` - name of policy 
* `description` - description of policy
* `startup` - run on startup?
* `enabled` - enable policy?
* `programs` - list of programs to apply policy to
* `rate` - rate to limit program to
* `burst` - burst to limit program to
* `prio` - priority to limit program to


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

--------------


### /ip_policy
Methods: GET, POST
#### GET: 
List all ip policies
In simpler format than /policy

params: 
* `page` - page number
* `per_page` - number of policies per page
Return: JSON of all policies

#### POST: 
Create a new ip policy

Body:
* `name` - name of policy
* `description` - description of policy
* `enabled` - enable policy?
* `startup` - run on startup?
* `transport` - transport to apply policy to (tcp, udp)
* `ip_src` - source ip to apply policy to
* `ip_dst` - destination ip to apply policy to
* `sport` - source port to apply policy to
* `dport` - destination port to apply policy to
* `rate` - rate to limit ip to
* `burst` - burst to limit ip to
* `prio` - priority to limit ip to

Return: JSON of new policy

--------------

### /ip_policy/:id
Methods: GET, PATCH, PUT, DELETE
#### GET:
Get a ip policy by id

Return: JSON of policy

#### PUT:
Update a policy by id

Body:
* `name` - name of policy
* `description` - description of policy
* `enabled` - enable policy?
* `startup` - run on startup?
* `transport` - transport to apply policy to (tcp, udp)
* `ip_src` - source ip to apply policy to
* `ip_dst` - destination ip to apply policy to
* `sport` - source port to apply policy to
* `dport` - destination port to apply policy to
* `rate` - rate to limit ip to
* `burst` - burst to limit ip to
* `prio` - priority to limit ip to


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
