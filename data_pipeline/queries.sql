
-- Query 1: Top 10 most expensive books
--  SELECT, ORDER BY, LIMIT


SELECT
    title,
    price_gbp,
    price_inr,
    rating
FROM books
ORDER BY price_gbp DESC
LIMIT 10;

-- Query 2: Highly rated books within a GBP price range
--  SELECT, WHERE, BETWEEN, ORDER BY


SELECT
    title,
    price_gbp,
    rating
FROM books
WHERE rating >= 4
  AND price_gbp BETWEEN 20 AND 40
ORDER BY rating DESC, price_gbp DESC;

-- Query 3: Distinct ratings available in the dataset
-- SELECT, DISTINCT, ORDER BY

SELECT DISTINCT
    rating
FROM books
ORDER BY rating;

-- Query 4: Books from selected categories
-- SELECT, WHERE, IN, JOIN, ORDER BY
SELECT
    b.title,
    b.price_gbp,
    b.rating,
    c.category_name
FROM books AS b
JOIN categories AS c
    ON b.category_id = c.category_id
WHERE c.category_name IN ('Fiction', 'Mystery', 'History')
ORDER BY c.category_name, b.title;

-- Query 5: Books with their category names
-- Demonstrates: SELECT, JOIN, ORDER BY
SELECT
    b.book_id,
    b.title,
    b.price_gbp,
    b.price_inr,
    b.rating,
    b.in_stock,
    c.category_name
FROM books AS b
JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY c.category_name, b.title;