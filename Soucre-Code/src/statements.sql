-- Create Stream for the pageviews topic
CREATE STREAM pageviews (
  USER_ID STRING,
  PAGE_URL STRING,
  TIMESTAMP TIMESTAMP
) WITH (
  KAFKA_TOPIC='datagen-pageviews',
  VALUE_FORMAT='JSON'
);

-- Query to select data from the stream (no need for EMIT CHANGES if you're using tests to validate once)
SELECT USER_ID, PAGE_URL, TIMESTAMP
FROM pageviews
LIMIT 10;  -- LIMIT to check a small batch of records
