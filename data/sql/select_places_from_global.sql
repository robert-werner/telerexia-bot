select row_number () over (order by weight asc), user_id, weight
from weights
order by weight asc