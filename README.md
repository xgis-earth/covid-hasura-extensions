# 2019-nCoV Hasura Extensions

## Environment Variables

The following environment variables must be defined for the database connection:

* COVID_DB_HOST
* COVID_DB_NAME
* COVID_DB_USER
* COVID_DB_PASS

## Docker Build & Push

```bash
docker build -t xgis/covid-hasura-extensions .
docker push xgis/covid-hasura-extensions
```

## Run Locally

```bash
docker run \
  --env=COVID_DB_HOST=secret \
  --env=COVID_DB_NAME=secret \
  --env=COVID_DB_PASS=secret \
  --env=COVID_DB_USER=secret \
  --publish=80:8000 \
  --detach=true \
  --name=covid-hasura-extensions \
  xgis/covid-hasura-extensions
```

## Hasura Deployment Configuration

### Country Airline Information: Action Definition

#### Query

```graphql
type Query {
  country_airline_info (
    country_code: String!
  ): [AirlineInfo]!
}
```

#### New Types

```graphql
type AirlineInfo {
  name: String!
  info: String!
  source: String!
  published: timestamptz!
}
```

#### Handler

http://query-country-airline-info/info

### Country News: Action Definition

#### Query

```graphql
type Query {
  country_news (
    country_code: String!
    limit: Int
    offset: Int
  ): [NewsItem!]
}
```

#### New Types

```graphql
type NewsItem {
  title: String!
  description: String!
  url: String!
  image_url: String
  category: String!
  language: String!
  country: String!
  published_at: timestamptz!
  source: String!
}
```

#### Handler

http://query-country-news/items

### Country Travel Information: Action Definition

#### Query

```graphql
type Query {
  country_travel_info (
    country_code: String!
  ): TravelInfo!
}
```

#### New Types

```graphql
type TravelInfo {
  info: String!
  restrictions: String!
  sources: String!
  published: timestamptz!
}
```

#### Handler

http://query-country-travel-info/info

### Johns Hopkins Data Refresh: Cron Trigger Event Definition

#### Name

refresh-johns-hopkins-data

#### Webhook

http://hasura-extensions/refresh/jhu

#### Cron Schedule

0 * * * *

_(hourly on the hour)_

#### Payload

```json
{
  "action": "refresh"
}
```

### Our World in Data Refresh: Cron Trigger Event Definition

#### Name

refresh-owid-data

#### Webhook

http://refresh-owid-data/refresh

#### Cron Schedule

0 * * * *

_(hourly on the hour)_

#### Payload

```json
{
  "action": "refresh"
}
```

### Population Counts Data Refresh: Cron Trigger Event Definition

#### Name

refresh-population-counts

#### Webhook

http://refresh-population-counts/refresh

#### Cron Schedule

0 0 * * 0

_(weekly on Sunday at midnight)_

#### Payload

```json
{
  "action": "refresh"
}
```

### Test Counts Data Refresh: Cron Trigger Event Definition

#### Name

refresh-test-counts

#### Webhook

http://refresh-test-counts/refresh

#### Cron Schedule

0 0 * * *

_(daily at midnight)_

#### Payload

```json
{
  "action": "refresh"
}
```
