SELECT * 
FROM weights
WHERE unix_time = (SELECT MAX(unix_time) from weights) AND user_id = {user_id}
ORDER BY unix_time DESC
LIMIT 2